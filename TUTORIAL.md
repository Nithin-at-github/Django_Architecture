# Tutorial: Django Layered Architecture vs. Traditional Django

This guide serves as a comprehensive tutorial to understand the differences between **Traditional Django (Fat Views & Generic CBVs)** and the **Layered Architecture (Repository-Service-View)** pattern commonly used in enterprise codebases.

To help you visualize these differences in action, we have implemented a side-by-side **Course Management** application under `/courses/` in this codebase.

---

## 1. High-Level Architectural Rationale

### Traditional Django Pattern
In standard Django, the framework encourages a rapid-development model where Class-Based Views (CBVs) or function views directly interact with the database ORM and perform business logic.

```
Request ──> View (ORM Queries, Form validation, DB mutations, error boundaries) ──> Response
```

* **Pros:** Extremely fast to write, minimal boilerplate, out-of-the-box support for CRUD using generic views.
* **Cons:** "Fat views" that merge HTTP concerns (cookies, headers, redirects) with business rules and database schemas. This makes unit testing views difficult because you always need a mocked HTTP context.

---

### Layered Architecture (Repository-Service-View)
To build maintainable, testable, and robust enterprise applications, we decouple the codebase into three single-responsibility layers:

```
Request ──> View (Thin) ──> Service (Business Logic) ──> Repository (ORM queries) ──> Database
```

1. **Repository Layer:** Encapsulates raw database queries and mutations (CRUD). The rest of the codebase is unaware of the exact database structure or query paths.
2. **Service Layer:** Houses the core business rules. It orchestrates transactional work (all-or-nothing changes) and manages query filters, sorting, and pagination.
3. **View Layer (Thin):** Responsible *only* for handling HTTP routing, parsing requests, rendering HTML templates, and initiating redirects. It delegates all database mutations and queries to the Service Layer.

---

## 2. Deep Dive: The Core Architectural Layers

### The Repository Layer (`app_base/repositories/base.py`)
The base repository (`PBBaseRepository`) encapsulates the standard Django ORM queries to isolate raw SQL or Django queries:
* `fetch_queryset()`: returns the base query.
* `get_by_id(pk)`: retrieves a single instance.
* `create()`, `update()`, `delete()`, `delete_multiple()`, `bulk_create()`: wraps mutations.

Concrete repositories subclass `PBBaseRepository` and override `fetch_queryset()` or define specific entity queries:

```python
# app_demo/repositories/course.py
class CourseRepository(PBBaseRepository[Course]):
    model = Course

    def create(self, **kwargs):
        # Auto-populating audit fields using user context bound to repository
        if self.user and self.user.is_authenticated:
            kwargs["created_by"] = self.user
        return super().create(**kwargs)
```

---

### The Service Layer (`app_base/services/base.py`)
The Service layer handles the core business decisions and coordinates transactions. 

#### A. Go-Style Error Tuples
To prevent database or connection exceptions from bubbling up to the views and triggering raw 500 errors, the service methods catch exceptions internally, log them, and return a tuple matching the Go programming language pattern:
`return result, error_message`

* **Success:** `(instance, None)`
* **Failure:** `(None, "Validation failed: code must be unique.")`

The view unpacks this tuple and translates any error message into a user-facing validation error or message banner.

#### B. Transaction Management
By programmatically controlling transactions inside the service layer using `transaction.atomic()` (via `run_transactional`), we ensure that multi-table operations are atomic. If a database insert fails halfway, the entire operation rolls back.

```python
# app_base/services/base.py
def run_transactional(self, func, *args, **kwargs):
    try:
        with transaction.atomic():
            result = func(*args, **kwargs)
            return result, None
    except Exception as e:
        self.logger.exception("Error executing transaction: %s", e)
        return None, str(e)
```

---

### The View Layer & Permission Mixin (`app_base/views/base.py`)
To prevent views from repeating service instantiation and user-binding code, we use a `PermissionServiceMixin`. It dynamically instantiates the service class and binds the `request.user` context to it:

```python
class PermissionServiceMixin:
    service_class = None

    def get_service(self):
        # Passes the active logged-in user to the service instance
        return self.service_class(user=self.request.user)
```

By subclassing `PermissionServiceMixin` in our base views (`PBBaseListView`, `PBBaseCreateView`, etc.), the views remain completely unaware of the ORM. They simply call the service methods and react to the returned `(result, error)` tuples:

```python
# View form validation handler
def form_valid(self, form):
    service = self.get_service()
    instance, error = service.create(form.cleaned_data)
    if error:
        form.add_error(None, error)  # Bind service exception as form error
        return self.form_invalid(form)
    return redirect(self.get_success_url())
```

---

## 3. Side-by-Side Code Comparison: Creating a Course

Let's compare the code between Path A and Path B for creating a new `Course` record:

| Aspect | Path A: Traditional Django | Path B: Layered Architecture |
| :--- | :--- | :--- |
| **View Class** | `class CourseStandardCreateView(CreateView):`<br>`    model = Course`<br>`    form_class = CourseForm` | `class CourseLayeredCreateView(PBBaseCreateView):`<br>`    model = Course`<br>`    service_class = CourseService`<br>`    form_class = CourseForm` |
| **Setting Audit User** | In view `form_valid()`:<br>`form.instance.created_by = self.request.user`<br>`return super().form_valid(form)` | Bound automatically in repository:<br>`kwargs["created_by"] = self.user`<br>View remains clean. |
| **Exception Boundaries** | Bubbled up to HTTP middleware. If DB constraint fails, crashes with 500 error unless caught manually in view. | Caught in `PBBaseService.run_transactional()`. Returns `(None, error)`. View displays inline form error. |
| **Database Call** | View performs `form.save()` which implicitly commits to database. | View calls `service.create(cleaned_data)`. Service calls `repository.create()`. |

---

## 4. Run the Side-by-Side Comparison

1. Make sure you are logged in (so audit tracking works).
2. Visit `/courses/` to view the **Django Architecture Playbook** comparison dashboard.
3. Test **Path A (Standard)** to see how generic CBVs perform full-page CRUD redirects.
4. Test **Path B (Layered)** to see identical templates performing identical operations, but completely driven by the clean, robust backend layers.
