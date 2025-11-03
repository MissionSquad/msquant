# NiceGUI Engineer’s Handbook (Vue.js/Python UI Framework)

## Summary and Overview

NiceGUI is an open-source Python framework for building web-based user interfaces that run in the browser or as desktop apps – all using pure Python code. It embraces a backend-first approach: your UI logic is written in Python, while NiceGUI handles the web frontend details under the hood. Built atop FastAPI (for the backend) and Vue.js with Quasar (for the frontend), NiceGUI allows developers to create rich interactive interfaces (buttons, forms, charts, 3D scenes, etc.) without writing any HTML/JS. This makes it ideal for dashboards, data visualization tools, robotics controls, IoT dashboards, or machine-learning apps – anywhere you want a responsive web GUI but prefer to work in Python.

Key features of NiceGUI include: real-time UI updates via WebSocket (no page reloads), a large set of ready-to-use components (from simple labels and buttons to data tables and plots), and straightforward state management with Python variables and events. NiceGUI supports multi-page routing, so you can build full multi-page web apps with distinct URLs. It also supports running in “native mode” (opening a desktop window via PyWebview) for an Electron-like experience. Under the hood, the framework uses a single Uvicorn server process with asynchronous handling, and maintains a persistent WebSocket to each client for user events and UI updates. In short, NiceGUI lets you focus on Python logic while it takes care of generating a smooth, modern UI in the browser.

**How to Use This Guide:** This handbook is a comprehensive resource for engineers building a web application with NiceGUI. We’ll cover setup, project structure, UI components (forms, tables, charts, etc.), event handling, integration of background tasks (for long-running jobs like model fine-tuning), and deployment strategies (with Docker). The goal is to provide a detailed roadmap so that you (or an AI coding agent) don’t have to guess any implementation details. The focus is entirely on NiceGUI usage — the domain-specific logic (like ML model quantization/fine-tuning) can be built on top of the robust UI foundation defined here.

Below is a structured Table of Contents for easy navigation of this handbook.

## Table of Contents

1.  **Introduction to NiceGUI**
2.  **Setting Up a NiceGUI Project**
    *   2.1 Installation (PIP, Docker, etc.)
    *   2.2 Project Structure and Template
3.  **NiceGUI Fundamentals**
    *   3.1 Backend-First Architecture
    *   3.2 Auto-Context and UI Creation
    *   3.3 Pages, Routing, and Sessions
4.  **Building the User Interface: Components and Layouts**
    *   4.1 Basic UI Components (Text, Images, Icons)
    *   4.2 Input Controls and Forms
    *   4.3 Buttons, Menus, and Dialogs
    *   4.4 Layouts: Rows, Columns, Cards, and Tabs
    *   4.5 Navigation and Multi-Page Structure
5.  **Events and State Management**
    *   5.1 Event Handling (Callbacks)
    *   5.2 Updating State and Data Binding
    *   5.3 Timers and Live Updates
    *   5.4 Background Tasks for Long-Running Processes
6.  **Displaying Data: Tables and Charts**
    *   6.1 Data Tables (`ui.table` and AG Grid)
    *   6.2 Charts and Graphs
    *   6.3 Streaming Logs and Metrics in the UI
7.  **Styling and Theming the Interface**
    *   7.1 Using Quasar Props and Tailwind Classes
    *   7.2 Custom CSS and Themes (Dark Mode)
8.  **Deployment and Configuration**
    *   8.1 Running in Development vs. Production
    *   8.2 Docker Deployment
    *   8.3 Environment Variables and Config Options
    *   8.4 Native Desktop Mode
9.  **Best Practices and Project Architecture**
    *   9.1 Code Organization and Modularization
    *   9.2 Avoiding Common Pitfalls (Blocking, etc.)
    *   9.3 Extending NiceGUI (Plugins and Custom Components)
10. **Summary and Next Steps**

---

## 1. Introduction to NiceGUI

NiceGUI is an “easy-to-use, Python-based UI framework” for creating interactive GUIs that render in your web browser. It wraps a modern Vue.js/Quasar frontend, but you as a developer write only Python code. NiceGUI abstracts away HTML/CSS/JavaScript, providing high-level Python functions to define UI elements and layouts. When you run a NiceGUI app, it starts a web server (by default on `http://localhost:8080`), and any browser can connect to see the UI. User interactions (button clicks, form inputs, etc.) are sent to your Python backend over a WebSocket, where your callbacks run. The resulting UI changes (like updating text or adding a new element) are then pushed back to the browser in real-time. This tight loop gives a smooth, desktop-like experience in the browser – without manual AJAX or page reloads.

**Why NiceGUI?** For many tasks, frameworks like Streamlit or Gradio offer simplicity but can become limiting in complex apps (state handling “magic” or single-page limitations). NiceGUI was created by developers who liked Streamlit’s ease but wanted more explicit control over state and a richer component set. With NiceGUI, you can build large-scale web applications with customized look-and-feel – essentially anything you could with a typical Vue/Quasar frontend, but driving it from Python. It’s suitable for dashboards, monitoring tools, robotics UIs, IoT control panels, smart-home apps, and ML model interfaces. In our use case (an interface for machine learning model quantization and fine-tuning), NiceGUI allows us to create forms for parameters, display training logs live, show charts of metrics, and even embed interactive 3D or image outputs – all directly from Python code.

**Technical Stack:** NiceGUI’s backend runs on FastAPI (ASGI) with Uvicorn, ensuring high performance and the ability to define additional REST endpoints if needed. The frontend uses Vue.js with the Quasar UI library, which provides a large collection of pre-styled components (the same underlying components NiceGUI exposes). Communication uses Socket.IO (WebSockets) to send events and data between Python and the browser. This means the UI is truly real-time – you can push updates to elements as data changes, and they reflect immediately on all connected clients. By default, NiceGUI runs a single server process (single Uvicorn worker) that can handle multiple client sessions asynchronously. This simplifies state management (no need to sync across workers) but also means if you have CPU-heavy tasks, you should run them asynchronously or off the main thread (more on that in Events and State Management).

In summary, NiceGUI offers the “nice” middle ground between simple-but-limited frameworks and full custom frontends: it’s Python-centric, easy to learn, yet powerful enough to build complex multi-page apps with custom components and styling. The following sections will guide you through using NiceGUI effectively for a production-grade project.

## 2. Setting Up a NiceGUI Project

### 2.1 Installation (PIP, Docker, etc.)

Getting started with NiceGUI is straightforward. You have multiple installation options:

*   **PyPI (pip):** The simplest route is to install the latest NiceGUI release from pip. For example:
    ```bash
    python3 -m pip install nicegui
    ```
    This will fetch the `nicegui` package and its dependencies. NiceGUI supports Python 3.9+ and runs on Linux, Windows, or macOS (since it’s pure Python with web backend). After installation, you can verify by importing `nicegui`.

*   **Conda-forge:** If you prefer Conda, NiceGUI is available on conda-forge as well. You can install it using `conda install -c conda-forge nicegui`.

*   **Docker Container:** The NiceGUI team provides an official Docker image on Docker Hub (`zauberzeug/nicegui`). This image packages a ready-to-run NiceGUI server environment. It’s useful for deployment or if you want to sandbox the app. For example:
    ```bash
    docker run -p 8080:8080 zauberzeug/nicegui
    ```
    This command will launch a container running the NiceGUI demo/docs app, accessible at `http://localhost:8080`. You can replace the container’s startup command with your own app (see “Docker Deployment” section). Using Docker ensures all dependencies (including Node for building frontend assets, if needed) are taken care of.

*   **From Source (GitHub):** For development or the latest features, you can clone the GitHub repo and run `poetry install` (or `pip install` from source). The repo even includes the code for the documentation site, which is itself a NiceGUI app – you can run `main.py` in the repo to browse the docs locally.

After installation, you’re ready to create your first NiceGUI app. The basic usage pattern is to import the `nicegui.ui` module and start defining the UI.

### 2.2 Project Structure and Template

While you can write a simple NiceGUI app in a single Python file, it’s best to organize your project especially as it grows. The maintainers provide an official NiceGUI Project Template (using Copier) to jump-start a well-structured app. This template sets up a recommended file layout, dependency management, and even CI/testing boilerplate. Key aspects of the project template:

*   It uses `pipx` and `Copier` to generate a new project. Once you have `pipx` and `copier` installed (see template README), you can generate a project with one command:
    ```bash
    pipx install copier  # if not already installed
    copier copy gh:zauberzeug/nicegui-template.git my_nicegui_app
    ```
    This will create a new folder `my_nicegui_app` with a ready-to-use NiceGUI app scaffold. It prompts you for project name and options (like whether to use Poetry, pre-commit, etc.).

*   The template organizes code into a Python package (module) and separates configuration. For instance, there will be a `main.py` to launch the app, a `pages/` module for page definitions, a `components/` module for custom UI components, etc. This modular structure makes it easier to maintain larger apps (we will discuss modularization in Best Practices).

*   It includes helpful dev tooling: optional Poetry for package management, pre-commit hooks, linting config (ruff, pylint), and a sample test setup. While testing NiceGUI apps is beyond our current scope, note that NiceGUI has a built-in testing approach using Playwright/pytest for UI tests. The template can generate a `tests/` directory with an example.

Using the official template is recommended to ensure you start with a known-good configuration. It saves time by including common settings (like `.gitignore`, Docker configs, etc.) that you’d otherwise set up manually. If you prefer not to use Copier, at least consider mirroring its structure: keep your UI code in organized modules, and use a virtual environment for dependencies.

**Example “Hello World” App:** Whether you use the template or not, the simplest NiceGUI program looks like this:

```python
from nicegui import ui

ui.label('Hello, NiceGUI!')  # display a text label
ui.button('PRESS ME', on_click=lambda: ui.notify('Button was pressed'))

ui.run()
```

When you run this script (`python3 main.py`), it starts the NiceGUI server and opens the interface at `localhost:8080`. You’ll see a label and a button; clicking the button triggers a notification toast. Notably, NiceGUI auto-reloads the page on code changes during development, so you can tweak the UI and see updates instantly. This rapid feedback loop is great for iterative development.

Next, we will dive deeper into how NiceGUI works and how to leverage its features in an engineering project.

## 3. NiceGUI Fundamentals

### 3.1 Backend-First Architecture

One of the core ideas of NiceGUI is that your Python code is the single source of truth for the UI. Unlike traditional web apps where front-end and back-end are separate, in NiceGUI you describe the interface in Python, and the library handles the synchronization between Python and browser. This backend-first approach means:

*   **State and Logic in Python:** You can use regular Python variables, data structures, and functions to control the UI. For example, if you have a list of items to display, you can loop over it in Python to create UI elements (no need to generate HTML). If a user clicks a button, it calls a Python function where you can directly modify variables or UI components. There’s no need to write a REST API or client-side JavaScript to handle events – NiceGUI sends all events to the backend for you.

*   **Web Details Abstracted:** The framework manages low-level web details (DOM updates, routing, etc.). It uses FastAPI/Starlette for the HTTP server and Socket.IO for continuous communication. Essentially, once you call `ui.run()`, your app is serving a web page that loads a Vue.js application. This Vue app knows how to connect back to your Python process and reflect the UI you defined. For example, if your Python says `ui.label("Hi")`, NiceGUI will send a message to the browser to create a new label component in the DOM.

*   **One Process, Async I/O:** By design, NiceGUI runs as a single Uvicorn process (single-threaded by default). It relies on FastAPI’s async capabilities to handle multiple requests concurrently. The persistent WebSocket allows the server to push updates at any time. This is efficient for dashboards, but note that CPU-bound tasks in Python will block other interactions if not handled asynchronously. We’ll address background tasks in a later section.

*   **FastAPI Integration:** Because it’s built on FastAPI, you can actually mount additional API routes or utilize FastAPI features if needed. For example, you could add `@ui.get('/api/data')` endpoints or use FastAPI’s dependency injection for database access in event handlers. In fact, the NiceGUI devs have an example of integrating NiceGUI with an existing FastAPI app, demonstrating this flexibility. By default, though, you don’t need to explicitly use FastAPI – `ui.run()` sets everything up.

In summary, the backend-first model means quick development (just write Python) and easier maintenance of state. There is no context-switching between languages or manually ensuring the frontend matches the backend state; NiceGUI does that for you. This model is also what allows NiceGUI to provide features like data binding (linking a Python variable to a UI element) and auto-reloading.

### 3.2 Auto-Context and UI Creation

When building UIs in NiceGUI, you will often see patterns like using `with` blocks or just calling `ui.element()` functions in sequence. NiceGUI uses an “auto-context” mechanism to know where to place each UI element you define. Here’s what that means:

*   **Implicit Parent Context:** You do not always need to specify which container or layout a new element should go into. NiceGUI keeps track of the current “open” container. For example, if you do `with ui.row(): ...`, all elements created inside that block will be children of the row. This is similar to how one might build a UI in Qt or other retained-mode GUIs. It avoids having to pass parent references around – you write intuitive, nested code and NiceGUI builds the nested DOM accordingly. If no explicit container is open, elements go to a default page context (usually the main page content or the specific page function if within one).

*   **Context Managers for Layout:** Many layout components (like `ui.row()`, `ui.column()`, `ui.card()`) can be used as context managers. For example:
    ```python
    with ui.card().classes('shadow-lg'):
        ui.label("Inside a card")
        ui.button("A button")
    ```
    This will produce a Card component (a Quasar Card) containing a label and a button. The `with` statement sets the card as the current context, so the label and button are added inside it. When the block ends, the context goes back to the parent (maybe the page).

*   **Auto Index Page:** If you don’t explicitly use `@ui.page`, all UI elements you create go into a shared page (the “index” at `/`). NiceGUI will automatically serve these on the main page for all users. This is convenient for single-page apps or quick scripts. However, for multi-user apps, a shared context means all users see the same state (if one toggles a switch it affects the single page instance). We’ll cover how to use multiple pages or per-user contexts in the next subsection.

*   **Example – Auto Context in Action:** Suppose you want a simple form with a label and input inside a vertical stack:
    ```python
    ui.label("User Info Form")
    with ui.column() as col:
        ui.label("Name:")
        name_input = ui.input()
        ui.label("Age:")
        age_input = ui.input(type='number')
    ui.button("Submit", on_click=lambda: process(name_input.value, age_input.value))
    ```
    In this snippet, because of the `with ui.column()`, the two labels and inputs are placed inside a column (stacked vertically). The “Submit” button is created after the `with` block, so it will be placed outside the column (in the parent context, here the page). The `as col` part isn’t strictly needed unless you want to refer to the column later (e.g., to hide/show it), but it shows you can get a reference to any element if needed.

The auto-context system makes code read like the UI layout – indentation in code corresponds to hierarchy in the UI. This greatly improves readability and maintainability of UI code. Just be mindful of context: if you accidentally create elements outside the intended `with`, they might end up in the wrong place. If needed, you can also manually specify parent-child relationships by keeping references and calling methods to add children, but this is rarely required thanks to context managers.

### 3.3 Pages, Routing, and Sessions

By default, NiceGUI applications behave like single-page apps with a shared state. However, NiceGUI provides a `@ui.page` decorator to define multiple pages (routes) and handle per-user state isolation. Here’s how pages and sessions work:

*   **Defining Multiple Pages:** You can attach `@ui.page('/path')` on top of a function to define a new page at that URL. For example:
    ```python
    @ui.page('/')
    def main_page():
        ui.label("Welcome to the main page")
        ui.button("Go to Dashboard", on_click=lambda: ui.open('/dashboard'))

    @ui.page('/dashboard')
    def dashboard_page():
        ui.label("This is the dashboard")
        # ... more UI ...
    ```
    In this case, visiting the root URL `/` triggers `main_page()` to build the UI for that page. If the user clicks the button, `ui.open('/dashboard')` will navigate their browser to the `/dashboard` route, which triggers `dashboard_page()` to run and build that page’s UI. Each page function creates its content fresh for each user session that navigates to it.

*   **Page Functions and State:** Each time a user opens a page, the decorated function runs in the context of that user’s session. This means any local state in that function (like variables or UI element objects) is specific to that user. If two users are on `/dashboard` at the same time, each had their `dashboard_page()` called separately. This gives session isolation, similar to how Streamlit handles multiple users. In contrast, if you don’t use pages and just declare UI at the module level, all users see and affect the same elements (shared global page). Both approaches are valid depending on your use case:
    *   A shared dashboard (without `@ui.page`) is useful for something like a monitoring screen on a big display, or if you intentionally want all clients to see identical updates (e.g., a real-time scoreboard).
    *   Per-user pages (with `@ui.page`) are appropriate for applications where each user might be doing something different (like configuring their own fine-tuning job without interfering with others).

*   **Routing and Navigation:** The `@ui.page` decorator not only registers the route, it also conveniently handles browser navigation. NiceGUI provides functions like `ui.open(path)` to programmatically send the user to a different page, and `ui.path` can retrieve the current path or parameters. You can also use anchor links (`ui.link`) if you want a clickable link to a route. Because NiceGUI uses an SPA-like client, navigation might not do a full page reload – it can often load the new page via the websocket connection, preserving some app context (especially in shared page scenario).
    You can pass route parameters in the URL and access them in the function signature. For example, `@ui.page('/user/[i:user_id]')` could accept an integer `user_id` which becomes a function argument.

*   **Session Lifecycle:** Underneath, each browser connection is a “client” in NiceGUI’s terms. NiceGUI can track clients and supports per-client data storage if needed (via `ui.client.storage`). By default, session cleanup (like when a user disconnects) will remove their UI elements. NiceGUI also emits life-cycle events (like `on_startup`, `on_shutdown` and `on_connect`, `on_disconnect` for clients) where you can run code if needed (not often required, but available).

*   **Example Use Case – Multi-Page LLM App:** For the ML model fine-tuning app context, you might have pages like:
    *   `/` – a landing page or a home with welcome text and navigation.
    *   `/configure` – a page with a form to set up a new quantization or fine-tuning job.
    *   `/monitor` – a page that displays current running jobs, logs, and metrics.
    *   `/results` – a page to visualize outputs or download artifacts.
    Each can be a function decorated with `@ui.page`. The user can navigate between them via a nav menu or buttons. Each user’s settings on `/configure` won’t interfere with another’s because each has their own session state. Meanwhile, `/monitor` could be designed either as a shared dashboard (showing all jobs) or user-specific (showing only that user’s jobs), depending on requirements – NiceGUI gives you the flexibility to implement it either way.

In summary, use `@ui.page` for any non-trivial app where you need multiple pages or separate user state. It will structure your app more cleanly and prevent cross-user state bleed. If you’re making a small single-page admin dashboard just for yourself, the simpler global page might suffice. But in an engineer’s project with many features, routing is your friend. NiceGUI’s routing is conceptually similar to Flask/FastAPI routing, so it should feel natural (just remember the output is a UI, not JSON).

**Tip:** You can mix static routes and NiceGUI pages. For instance, you could serve a static HTML at `/about` via FastAPI and have NiceGUI pages for the interactive parts. But often it’s easier to just create a NiceGUI page for consistency.

## 4. Building the User Interface: Components and Layouts

Now we delve into the practical aspect: creating UI elements with NiceGUI. The library comes with a rich collection of UI components that cover most needs, all accessible via the `ui` module. We’ll cover different categories of components and how to use them, from basic text to complex charts.

### 4.1 Basic UI Components (Text, Images, Icons)

These are the fundamental building blocks to display information:

*   **Labels and Text:** Use `ui.label("Text")` to display a simple piece of text. This is one of the simplest components – effectively a span of text. You can control its appearance using Tailwind classes or Quasar props (covered in Styling). For multiline or formatted text, NiceGUI offers `ui.markdown("Some *Markdown* **text**")` which will render Markdown content (useful for bold, links, etc.). There’s also `ui.html("<b>raw HTML</b>")` if needed, but generally Markdown or combinations of labels is safer.

*   **Icons:** NiceGUI can display material design icons (through Quasar). For example, `ui.icon('home')` will show a home icon. These icons can be styled (size, color) via classes or props. They are useful inside buttons or labels to enhance UI clarity.

*   **Images:** To show an image, use `ui.image('path_or_url.png')`. The source can be a local file path, a URL, or even a base64 data URI. You might use this to show a logo or results like charts exported to images. For dynamic images (e.g., updated plot snapshots), you can keep a reference to `ui.image` and change its `.source` attribute, then call `image.update()`. There’s also `ui.interactive_image` for more complex use (like a canvas with events), but for static images `ui.image` suffices.

*   **Headings/Sections:** While not explicit separate components, you can just use `label` or `markdown` for headings. For example, `ui.label("Section Title").classes('text-xl font-bold')` would make a larger bold text (using Tailwind utility classes for styling). Markdown can do headings with `#` as well.

These basic elements are straightforward. For instance, a header for your app could be:

```python
ui.icon('insights').classes('text-2xl')
ui.label('LLM Fine-Tuning Dashboard').classes('text-2xl')
```

Which places an icon and a label (you might want them in a row or with some spacing, which leads us to layouts next). Keep in mind that NiceGUI automatically ensures these appear in the right context as per your code structure.

### 4.2 Input Controls and Forms

Most apps require user input. NiceGUI provides form elements analogous to HTML form inputs or desktop GUI widgets:

*   **Text Input:** `ui.input()` creates a text input box. You can specify a placeholder (`ui.input(placeholder="Enter name")`), an initial value, and a label (`ui.input(label="Name")` renders a floating label). The `.value` property of the input holds the current text, which you can read or even bind to a variable (more on binding later). If you want to respond as the user types, you can attach an `on_change` or use events (like `.on('keydown.enter', ...)` to detect when Enter is pressed). By default, text inputs are single-line; for multi-line use `ui.textarea()` (if available) or a larger input with a prop.

*   **Number Input/Slider:** You can either use `ui.input(type='number')` for numeric input or use dedicated controls:
    *   `ui.slider(min=0, max=100, value=50)` gives a slider bar for selecting a number in range.
    *   `ui.number(label="Amount", value=10)` – NiceGUI might have a specific number input (or you can just treat an `ui.input` as number by reading `float(input.value)` etc).
    For ranges or more complex inputs, consider a combination of slider and input.

*   **Checkbox & Switch:** `ui.checkbox("Label", value=True)` creates a checkbox (tick box). `ui.switch("Label", value=False)` creates a toggle switch (functionally similar to checkbox but looks like a switch). These components have a `.value` (boolean) and can have `on_change` handlers.

*   **Radio Buttons:** For selecting one of many options, you can use `ui.radio` group. Typically, you create a `ui.radio` for each option but share a common Python variable or utilize value binding. NiceGUI might offer something like `ui.radio(['Option A', 'Option B'], value='Option A')` to automatically create a radio group (this depends on the API). If not, you can compose it: e.g.,
    ```python
    selected = {'option': 'A'}
    def set_opt(val): selected['option'] = val
    ui.radio('Option A', value=True, on_change=lambda: set_opt('A'))
    ui.radio('Option B', value=False, on_change=lambda: set_opt('B'))
    ```
    and enforce only one true at a time manually. (Check NiceGUI docs for a better pattern – often there’s a `ui.select` which might cover this.)

*   **Dropdown Select:** Yes, `ui.select` is available for a dropdown menu of choices. For example:
    ```python
    ui.select(options=['Small', 'Medium', 'Large'], value='Medium', label='Size')
    ```
    This will show a material-design select box. You can retrieve the selection via `.value`. There’s also `ui.combo_box` or `ui.autocomplete` (if Quasar’s QSelect is used, it supports filtering as you type). The NiceGUI docs mention that `ui.select` options can be updated dynamically (you can call `select.update()` after changing its options list).

*   **Chips Input:** NiceGUI provides `ui.input_chips` which is an input field allowing multiple entries as chips (useful for tags or list of items). For example, `ui.input_chips(label="Keywords")` lets user enter multiple keywords separated by comma or confirm each with enter, each becoming a “chip”.

*   **Date/Time Pickers:** Check if NiceGUI wraps Quasar’s date/time components. Often there might be `ui.date()` or `ui.datetime()`. If not directly, you could call a `ui.input(type='date')` as a basic HTML date input. But likely NiceGUI has something like `ui.date_picker`.

*   **File Upload:** `ui.upload()` allows user to upload files. When a file is uploaded, you can handle it (perhaps an `on_upload` callback). NiceGUI likely stores the file in a temporary location or in memory and provides it to you. For example:
    ```python
    ui.upload(label="Upload dataset", on_upload=lambda e: handle_file(e.content))
    ```
    where `e.content` might be the file bytes or file path.

All these input elements can be combined to build forms. You might group them in a `ui.form()` container (if provided) or simply in a `ui.column` with a submit button. Form submission isn’t a distinct concept as in traditional HTML (no form POST); instead, you just attach an `on_click` to a button that reads all the input values and processes them. For instance, to handle a configuration form for fine-tuning, you could do:

```python
model_input = ui.input(label="Model Name")
lr_input = ui.number(label="Learning Rate", value=1e-4)
epochs_input = ui.slider(min=1, max=10, value=3, label="Epochs")
ui.button("Start Fine-Tuning", on_click=lambda: start_job(model_input.value, lr_input.value, epochs_input.value))
```

This collects values and calls `start_job` with them. You might want to add validation – e.g., ensure model name is not empty. You can do that in the callback (and maybe use `ui.notify` or `ui.tooltip` to inform user if something is wrong).

One more neat feature: NiceGUI supports data binding on these inputs. For example, you can bind the `.value` of an input to a variable or even another element’s property. We’ll discuss this in Events and State Management, but keep in mind it can reduce boilerplate if you have many inputs whose values you want to keep track of.

### 4.3 Buttons, Menus, and Dialogs

Interactive elements like buttons and menus trigger actions in your app:

*   **Buttons:** The staple of any UI. `ui.button("Label", on_click=func)` creates a clickable button. You can customize its style (e.g., `ui.button("Save", on_click=save).props('outline')` for an outlined style, or use `.classes('...')` to add Tailwind classes). Buttons can also have icons: `ui.button('Refresh', on_click=refresh).props('icon=refresh')` would show a refresh icon on the button (assuming Quasar’s QBtn which supports an `icon` prop). Common uses: form submission, starting/stopping processes, navigation (`on_click=lambda: ui.open('/somepage')`), etc.

*   **Link Buttons:** If you want a button that’s actually a link, you can use `ui.link("Go to Docs", url="https://nicegui.io")`. That opens an external/internal link. For internal navigation, as mentioned, `ui.open()` in a normal button is fine.

*   **Menus and Context Menus:** If you have multiple actions, you can use `ui.menu()` to create a menu bar or dropdown menu. NiceGUI likely wraps Quasar’s QMenu and related components. For example:
    ```python
    with ui.menu() as main_menu:
        ui.menu_item("File")
        ui.menu_item("Edit")
    ```
    But a more useful one is context menu (right-click menus). The docs mention `ui.context_menu` to attach a menu that appears on right-click of some element. You might not need this immediately, but it’s good for power-user features or options on table rows, etc.

*   **Dialogs (Modals):** NiceGUI supports dialogs for pop-up content. You can create one via `with ui.dialog() as dialog: ...` to define the dialog’s content, then show it with `dialog.open()`. Inside the `with ui.dialog():`, you would place the dialog UI elements (text, buttons). For instance:
    ```python
    with ui.dialog() as confirm_dialog:
        ui.label("Are you sure you want to delete this model?")
        with ui.row():
            ui.button("Yes", on_click=lambda: do_delete() or confirm_dialog.close())
            ui.button("Cancel", on_click=confirm_dialog.close)
    ui.button("Delete Model", on_click=confirm_dialog.open)
    ```
    This pattern creates a hidden dialog and a button that opens it. NiceGUI handles the overlay and centering. Dialogs are great for confirmation prompts or additional forms without navigating away.

*   **Notifications & Toasts:** You saw `ui.notify("message")` earlier – this is a quick toast message that appears and fades out. It’s very handy for status info (e.g., “Job started successfully”). It might also indicate errors or success by passing a color or icon (`ui.notify("Error: invalid input", color="negative")` perhaps).

*   **Drawer / Sidebar:** If your app has a side navigation or settings panel, you can use `ui.drawer()` to create a sidebar that can slide in. Quasar has a drawer component; NiceGUI likely exposes it. You might tie a button (like a “Menu” ☰ icon) to open/close the drawer via `drawer.toggle()`.

**Tip:** All these interactive components (buttons, menu items, etc.) use event callbacks. You can define the callback as a normal `def` or `lambda`. If the callback needs to do something in the UI (like show/hide elements, update text, etc.), just do it in Python – thanks to the live connection, any changes you make to UI elements (like `label.text = "new"` and `label.update()`) will be sent to the browser immediately.

### 4.4 Layouts: Rows, Columns, Cards, and Tabs

Good layout is critical to a clean UI. NiceGUI, via Quasar, provides flexible layout components:

*   **Horizontal vs Vertical:** Use `ui.row()` to arrange child elements horizontally (in a flex row). Use `ui.column()` to stack them vertically. These are your go-to for basic layout. They correspond to Quasar’s QRow/QCol or simply flex CSS. You can nest rows/columns to create grids.

*   **Cards and Containers:** `ui.card()` places a Quasar Card – essentially a panel with some padding and an optional outline. It’s great for grouping related elements. You might put an entire form or a chart inside a card. Cards can have titles, sections, etc., but in NiceGUI you just compose it yourself (e.g., first element in card could be `ui.label("Card Title").classes('text-lg')`).

*   **Tabs:** For tabbed content, NiceGUI has `ui.tab` components. Typically you create a `ui.tabs()` container and then add `ui.tab()` items. For example:
    ```python
    with ui.tabs() as tabs:
        ui.tab('Logs'); ui.tab('Metrics')
    with ui.tab_panels(tabs, value='Logs'):
        with ui.tab_panel('Logs'):
            ui.label("Training log here...")
        with ui.tab_panel('Metrics'):
            ui.label("Metrics charts here...")
    ```
    This would create a tab bar with “Logs” and “Metrics”, and corresponding panels that show on selection. The `ui.tab_panels(tabs, ...)` links the panels to the tab set. The API might slightly differ, but conceptually that’s how to manage tabs. Tabs help to organize content without separate pages – useful if the content is closely related or you want quick switching (like different views of the same data).

*   **Grid and Columns Size:** For more complex responsive layout, Quasar’s grid system can be used. NiceGUI might have `ui.row().classes('items-stretch')` and then inside it multiple `ui.column().classes('w-1/2')` to make two columns, etc. You can also use `ui.grid(columns=3)` or something similar (the docs hint at an element wrapping AG Grid, but for general grid layout, using Tailwind classes for width or Quasar’s `<q-col>` with specified sizes might be needed).

*   **Spacing and Alignments:** Use Tailwind utility classes (already included with NiceGUI) to adjust spacing. For instance, `.classes('mt-4')` to add margin-top, `.classes('justify-center')` on a row to center children, etc. Quasar props might also allow alignment: e.g., `ui.row().props('align=center')`.

*   **Example Layout:** Suppose we want a top bar with a title and a content area below. We could do:
    ```python
    with ui.row().classes('items-center justify-between'):
        ui.label("My App").classes('text-2xl')
        ui.button("Help", on_click=show_help_dialog)
    ui.separator()  # a horizontal line
    with ui.row().classes(''):
        with ui.column().classes('w-1/3'):
            ui.label("Sidebar content")
        with ui.column().classes('w-2/3'):
            ui.label("Main content here")
    ```
    This is a simplistic example. For a real app, you might use a more responsive approach or drawers instead of a fixed sidebar. But it shows using nested rows/columns to achieve structure.

*   **Dialogs and Overlays in Layout:** Note that dialogs and menus aren’t part of the normal layout flow (they float over it). So you typically define them at the end of your page function (or globally) so they’re available but not interfering with main layout.

### 4.5 Navigation and Multi-Page Structure

We touched on pages earlier. In terms of UI building, how do you allow users to navigate your app? Some strategies:

*   **Navigation Bar:** You can create a top navigation bar with buttons or links for each page. For example, at the top of each page function, you might include:
    ```python
    with ui.row().classes('bg-gray-200 p-4'):
        ui.link('Home', '/')
        ui.link('Configure Model', '/configure')
        ui.link('Monitor Jobs', '/monitor')
    ```
    This would render as simple text links. You could style them as Quasar buttons by doing `ui.button("Configure", on_click=lambda: ui.open('/configure'))` for more button-like feel. There’s also `ui.button_link` possibly, but either works.

*   **Sidebar Menu:** Alternatively, a sidebar (drawer) with menu items for pages is common. You can make a drawer that’s always visible (if screen wide enough) or toggled by a menu icon for mobile. The drawer content would have `ui.link` or `ui.button` items to open pages. NiceGUI might support a “menu item” component that looks good in a drawer (like `ui.menu_item("Dashboard", on_click=...)`).

*   **Programmatic Navigation:** Sometimes you navigate in code after an action. E.g., after a user submits a form, you might want to redirect them to the monitoring page. You can call `ui.open('/monitor')` in your event handler to send them there. Just ensure that route/page exists.

*   **Page Titles:** By default, the browser tab title might be “NiceGUI” or whatever you set in `ui.run(title="My App")`. You can update it per page if needed by using JavaScript or maybe NiceGUI has some support (not critical though).

*   **Maintaining State Between Pages:** Since each page function is separate, you might need to pass data between them (like an ID of a newly created job from configure -> monitor). You can do this by:
    *   Storing in a global Python dict keyed by session or globally if applicable.
    *   Using query parameters in URL (e.g., navigate to `/monitor?job=123` and parse `ui.get_query()`).
    *   Or using `ui.client.storage` which can hold data in the browser across pages (like local storage, but NiceGUI provides an API). NiceGUI’s persistence features allow per-user storage that persists across sessions as well.
    In many cases, simply re-computing or re-fetching data on the new page is fine (like the monitor page could just load all current jobs from a global list or database when it opens, rather than getting it from the previous page).

*   **Authentication (if any):** NiceGUI doesn’t include auth out-of-the-box, but you can use FastAPI’s authentication dependencies, or roll a simple login page and restrict other pages by checking a logged-in flag. Discussion of auth would be beyond scope, but be aware it’s something you’d need to handle (possibly via a custom route or using `ui.open` to send to login if not logged in).

By carefully constructing your navigation and using `@ui.page` for structure, you ensure the user can smoothly move through the app. It’s good to test that the browser’s back button works as expected – with NiceGUI pages, it should (since routes are actual URLs), but if you rely solely on `ui.open`, confirm that state is maintained or reloaded appropriately.

Now that we have the building blocks of the UI defined, let’s explore how to handle user interactions and dynamic behavior in the next section.

## 5. Events and State Management

Interactivity is where NiceGUI shines – responding to user input and updating the interface dynamically. In this section, we’ll discuss how to write event callbacks, manage application state, and ensure the UI reflects state changes (using explicit updates or NiceGUI’s binding system). We’ll also cover scheduling updates with timers and running background tasks to keep the UI responsive.

### 5.1 Event Handling (Callbacks)

Every interactive UI element in NiceGUI allows you to specify callback functions that execute when an event occurs. Since the UI is driven by the backend, these callbacks run in Python:

*   **Basic Callbacks:** Most components have convenience parameters for common events. For example, `ui.button("Click me", on_click=my_function)` will call `my_function` when the button is clicked. Similarly, `ui.checkbox("I agree", on_change=on_toggle)` triggers on any change (checked/unchecked). The callback can be a function or lambda. If you need to pass arguments, you can use `functools.partial` or lambdas capturing variables. For instance:
    ```python
    ui.button("Delete", on_click=lambda: delete_item(item_id))
    ```
    This calls `delete_item(item_id)` when clicked. Just be careful with lambdas in loops (common Python caveat – ensure the lambda captures the current value).

*   **Event Objects:** Some events will pass an event object to the callback with additional data (if the signature expects it). For example, file upload or keyboard events might pass info about the key or file. The NiceGUI documentation shows an example for input keydown event: `ui.input().on('keydown.enter', handle_enter)`. The handler might get the key event data. But for most `on_click` or `on_change`, your function doesn’t need parameters, or you can retrieve state via captured variables/UI element references.

*   **UI Updates in Callbacks:** Within a callback, you can perform any Python actions (launching a script, writing to disk, etc.) and also modify the UI. For example, suppose a button starts a training process – you might want the button to disappear or disable once clicked. In the callback, you could do:
    ```python
    button.disable()  # mark it disabled (greyed out)
    button.update()
    ```
    Then re-enable when done. Or update a status label: `status_label.text = "Training started..."; status_label.update()`. The `.update()` method is crucial – it tells NiceGUI to send the updated state of that element to the client. Some properties, like `.value` of inputs or `.checked` of a checkbox, might auto-sync, but in general if you change an element from code, call `update()` on it (or `ui.update(element)` could be a utility).

*   **Long-running callbacks:** If your callback might take a while (say, launching a subprocess and waiting), you should offload it (see Background Tasks below). If you don’t, the UI will freeze for all users while that callback is running, because the single-thread event loop is busy. A common pattern is to quickly spawn a thread or task in the callback and return, so the UI remains responsive.

*   **JavaScript events:** NiceGUI allows listening to arbitrary DOM events via the `.on()` method. For example, `ui.input().on('blur', func)` if you want to catch when an input loses focus. But most of the time, the provided `on_click`/`on_change` cover what you need.

*   **Example:** Suppose we want to update a chart when a dropdown selection changes:
    ```python
    chart = ui.line_plot(...)  # hypothetical chart component
    def update_chart():
        new_option = dropdown.value
        data = fetch_data_for(new_option)
        chart.options = {"series": [{"data": data}]}  # update options
        chart.update()
    dropdown = ui.select(options=['Option1','Option2'], on_change=update_chart)
    ```
    This way, whenever the user picks a different option, the callback fetches new data, updates the chart’s series, and calls `update()` on the chart to re-render it. (If using the Highcharts component, it might require calling `chart.update()` method specifically – we’ll cover charts soon.)

### 5.2 Updating State and Data Binding

Managing application state (the variables and data that represent the UI’s content) is a central task. NiceGUI offers features to make this easier:

*   **Manual State Management:** The straightforward way is to keep Python variables or data structures for your state. For instance, a global dictionary of running jobs, or a list of log lines. You update these in callbacks and then manually refresh parts of the UI. This is essentially what you’d do in a normal backend – treat the UI as a view onto your data. Whenever data changes, you push updates to UI elements. For example:
    ```python
    progress = 0
    progress_bar = ui.linear_progress(value=0)

    def on_tick():
        global progress
        progress += 1
        progress_bar.set_value(progress)
        progress_bar.update()
        if progress >= 100:
            timer.deactivate()
    timer = ui.timer(interval=1.0, callback=on_tick)  # increment progress every 1s
    ```
    Here `progress` is a Python state variable. Each tick we update it and then call `set_value` on the UI element followed by `update()`. This explicit method works fine and is clear.

*   **Bindable Properties (Data Binding):** NiceGUI can reduce boilerplate by binding UI components to Python objects. The framework introduced bindable properties that follow an MVVM-style pattern. Essentially, certain UI element attributes (like a label’s text, or an input’s value) can be tied to an attribute of a Python object. When one changes, the other updates automatically. Under the hood, NiceGUI’s `BindableProperty` mechanism uses descriptors and event wiring. An example from the NiceGUI docs (and the Medium article) is:
    ```python
    from nicegui.binding import bind_from, BindableProperty
    class Person:
        name = BindableProperty()

    p = Person()
    name_input = ui.input()
    bind_from(name_input, 'value', p, 'name')
    ```
    Now if `p.name` changes, the input’s value updates, and if the user types something, `p.name` updates. This can be very powerful – especially for complex forms or when multiple elements reflect the same state. In our context, if we had a class representing a training job with a `status` property, we could bind a UI label’s text to that status. As the job progresses (from code, we set `job.status = "50%"`), the label on the UI would update without calling `update` manually.

    The Medium article showed a more advanced use: a custom `BindableList` to bind a list of items to a UI list component, so that adding/removing items in Python automatically re-renders the list UI. That example is advanced, but it illustrates that almost any UI element’s state (items in a list, selected tab, etc.) can be bound.

    For typical use, you might use simpler helper functions:
    *   `element.bind_value_to(model, 'attr')` or `element.bind_text_to(...)` as shorthand if provided.
    *   E.g., `checkbox.bind_value_to(settings, 'enable_logging')` would keep `settings.enable_logging` in sync with the checkbox’s checked state.
    *   Conversely, `table.bind_rows_from(data_model, 'records')` could update a table when `data_model.records` list changes (hypothetical example).

    Data binding is optional; you can always manually update values. But it’s worth using for forms and dynamic content to avoid forgetting a UI update call.

*   **Session vs Global State:** Decide what needs to be per-user. If using `@ui.page`, any variables inside the page function will get re-created per session. If you need a global state (like a list of all jobs or a global log), define it globally and protect access if needed (since the single thread ensures atomicity unless you use threads, in which case use locks). NiceGUI also has a notion of general vs user-specific data: it supports general (shared) and per-user storage. For example, `ui.client.storage.user` vs `ui.client.storage.general` might exist. You can use these to persist state in browser storage or server memory.

*   **Refreshing UI – `ui.update` and `ui.refreshable`:** Besides calling `update` on individual elements, NiceGUI provides a decorator or context `ui.refreshable`. If you mark a function as `@ui.refreshable`, you can call that function and it will automatically update its output in the UI when underlying data changes. This is similar to how Streamlit re-renders, but under your control. For instance:
    ```python
    @ui.refreshable
    def show_summary():
        ui.label(f"Jobs completed: {jobs_completed}")
        ui.label(f"Last run: {last_run_time}")
    # ... somewhere later
    jobs_completed += 1
    show_summary.refresh()  # will update the two labels inside
    ```
    This ensures the snippet inside `show_summary` re-runs and updates the labels. It’s a structured way to update multiple elements together.

In practice, you might start with manual updates and adopt binding for cases where it simplifies the code. For our ML app example, we could have a global dict `jobs` where we store info. A background thread updates `jobs[job_id]['progress']`, and a UI timer periodically reads that and updates a progress bar. Or we bind the progress bar’s value to `jobs[job_id].progress` directly if using an object. Both approaches can work; binding just abstracts the glue.

### 5.3 Timers and Live Updates

Live updating the interface is often needed for dashboards (e.g., periodically refresh metrics, or update a chart as data flows in). NiceGUI offers the `ui.timer` utility for this:

*   **`ui.timer`:** `ui.timer(interval=seconds, callback=my_func, once=False)` creates a timer that calls `my_func` every `interval` seconds. By default, it repeats; if you set `once=True` it would only run once after the delay (like a timeout). This is implemented in the browser (using JS `setInterval` or similar via Quasar) and triggers a call to the Python backend on each tick. Use timers sparingly (an update every 0.01s is possible per features, but that will generate a lot of traffic— in practice keep it reasonable like 0.5s+).

    **Example use:** Update GPU utilization label every 5 seconds:
    ```python
    gpu_label = ui.label("GPU: ?")
    def refresh_gpu():
        util = get_gpu_utilization()  # a function that reads NVML or similar
        gpu_label.text = f"GPU Utilization: {util:.1f}%"
        gpu_label.update()
    ui.timer(5.0, refresh_gpu)
    ```
    This will call `refresh_gpu` every 5 seconds, and the label will show updated info. It’s essentially like a loop in the UI.

*   **Manual loop using asyncio:** Alternatively, since NiceGUI is async, you could create an `async def background_task()` that loops with `await asyncio.sleep(5)` and does updates. But NiceGUI’s timer is easier as it handles scheduling the callbacks on the main thread appropriately.

*   **Live Charts or Logs:** If you want to stream logs line by line to a text box, one method is to have a timer that checks a buffer and appends new lines to a `ui.label` or `ui.log_area` if such exists. Another approach is using an async generator and `ui.stream` if something like that exists. However, a simple repeating callback to pull new logs and update a `ui.markdown` or `ui.preformatted` text is fine.

    For charts that update (like a real-time graph of loss vs epoch), you can either:
    *   Update the data series in the callback (like our earlier example using `chart.update()`). Highcharts can handle dynamic updates if you call its update function or add points via series API – but from Python side, you likely recompute the option dict and call `chart.update()`.
    *   Or re-create the chart element each time (less ideal). So timers + chart references is the way.

*   **Stopping updates:** The timer object returned by `ui.timer` has methods like `deactivate()` to stop it. You can conditionally call that (as seen in the progress example pseudo-code). If you don’t stop a repeating timer, it will keep going as long as the session is open (which is fine for periodic updates).

*   **Throttling/Performance:** If you find that frequent updates flood the UI (e.g., printing every log line as it comes could overwhelm), you might aggregate updates (update UI with batches of lines rather than one line at a time), or use a slightly longer interval. Also consider client-side rendering – for logs, maybe easier is to use a `<pre>` block that you keep appending text to (the browser can handle some text addition every second or so no problem). NiceGUI is efficient with WebSocket, but every update is a message, so keep payloads moderate.

### 5.4 Background Tasks for Long-Running Processes

In our scenario, certain operations (like fine-tuning a model) can take minutes or hours. We must ensure the UI remains responsive during those operations and that we can update the UI with progress. NiceGUI is based on FastAPI and Uvicorn, so while it can handle async I/O easily, a long CPU-bound task in a callback will block the event loop. Strategies to handle this:

*   **Use Threads or Async IO:** You can offload work to a separate thread or process. For instance, Python’s `threading.Thread` or an `asyncio.to_thread` call. If you spawn a thread for training, that thread can run concurrently while the main thread continues serving UI. You’ll need to periodically communicate from that thread to the main thread (maybe by updating shared variables and using timers on main thread to check them, or by scheduling callbacks via NiceGUI).

    FastAPI (and thus NiceGUI) also has a mechanism: you can inject a `BackgroundTasks` object (from fastapi) to schedule background tasks. However, in NiceGUI specifically, they have a helper: the search snippet suggests a `background_tasks.create()` method in NiceGUI to run an async function in background. Possibly `nicegui.background_tasks.create(coro)` returns a task handle. You could use this to start an async job (like an `async def train_model(): ...` that uses `await` for any I/O). The background task will run, and you can periodically send UI updates from it using `ui.run_javascript` or perhaps by modifying UI elements if thread-safe.

    If using plain threads, ensure thread-safe access to NiceGUI. Typically, updating UI elements from a background thread might not directly be safe. It’s wise to funnel UI updates back to the main thread. One simple way: use `ui.notify` from the thread – NiceGUI might queue it to main automatically, but I would not assume that. Instead, you can have the thread add messages to a `queue.Queue`, and a `ui.timer` on main thread polls that queue and applies updates.

*   **Example (Threaded Task):**
    ```python
    import threading
    progress = 0
    status_label = ui.label("Status: Idle")
    def train_model(params):
        global progress
        for epoch in range(1, params.epochs+1):
            # ... training logic ...
            progress = epoch / params.epochs * 100
            # Here instead of directly updating UI, just update a shared var
        # when done, maybe store results or set a flag
    def start_training():
        status_label.text = "Training started"
        status_label.update()
        threading.Thread(target=train_model, args=(current_params,)).start()
    ui.button("Start Training", on_click=start_training)
    # Timer to update UI progress
    def refresh_status():
        status_label.text = f"Progress: {progress:.0f}%"
        status_label.update()
        if progress >= 100:
            status_label.text = "Training completed"
            status_label.update()
            timer.deactivate()
    timer = ui.timer(1.0, refresh_status)
    ```
    This is a rudimentary pattern. A more sophisticated approach is to incorporate the updating within the thread: NiceGUI might allow calling `ui.update()` from any thread and it queues it. Actually, NiceGUI likely collects all UI changes from event loop and sends them at end of cycle, so cross-thread might not be directly supported. Hence the decoupling with shared state and timer is a safe bet.

*   **NiceGUI Background Task Utility:** If `background_tasks.create` exists as per docs, you could do:
    ```python
    async def train_model_async(params):
        for epoch in range(...):
            # do training for an epoch (maybe using await for heavy I/O)
            ui.notify(f"Completed epoch {epoch}")
        ui.notify("Training done!")
    background_tasks.create(train_model_async(params))
    ```
    This would run in background. The `ui.notify` calls within should be thread-safe if it’s actually still on the event loop (since async tasks run on the same loop, just concurrently). That would be ideal for tasks that can be written in async style (if mostly I/O or if using something like `await asyncio.to_thread` for CPU work).

*   **Progress Feedback:** For long tasks, providing feedback is key. Some options:
    *   Update a progress bar or percentage label periodically (as shown).
    *   Stream log output to a text area live. If you have the process output (say from `subprocess.Popen`), you can read from it in a thread and append lines to a list; use timer to flush to UI.
    *   Use `ui.notify` for milestone updates (simple but not persistent on screen).
    *   Change button text or disable it (“Running…”).
    *   Provide a “Cancel” button: that could set a flag the background task checks to break out.

*   **Example – Visualizing Logs:** If fine-tuning prints logs, you can capture them. E.g., if using an external script, launch it with `subprocess.Popen(..., stdout=PIPE)`. Then spawn a thread to read the stdout line by line. Each line, add to a global list `logs.append(line)`. In UI, have a `ui.markdown` or `ui.log_area` that periodically updates to include new lines:
    ```python
    log_md = ui.markdown("", highlight=False)  # no highlight for raw text
    last_seen = 0
    def update_logs():
        nonlocal last_seen
        if last_seen < len(logs):
            # append new lines
            new_text = "\n".join(logs[last_seen:])  
            log_md.content += ("\n" + new_text)
            log_md.update()
            last_seen = len(logs)
    ui.timer(1.0, update_logs)
    ```
    This naive approach just appends text. You might want to limit log size or scroll. Alternatively, use `ui.preformatted()` if available to keep text spacing.

*   **Monitoring System Metrics:** Similar approach – use a background thread or timer to periodically poll system metrics (CPU, GPU, memory). For GPU, if NVML is installed, `pynvml` can query usage quickly. Put those in a global and update UI with a timer. You could use a chart to plot historical usage: store a `deque` of last N values and update a line chart’s series each tick with the new list.

*   **Concurrency Considerations:** Because NiceGUI uses one server process, threads share memory – which is fine, just protect shared data if needed. If you expect heavy CPU usage, note that Python threads won’t actually run in parallel due to GIL (unless your computations release GIL, like NumPy operations do, or you use `multiprocessing`). For pure Python training loops, consider using `multiprocessing` to truly parallelize or just accept that the UI will be a bit sluggish (though in an async model, one CPU-bound thread can starve others). Another trick: use an external process for training and communicate via file or socket, to keep the UI process light.

*   **Cancelling tasks:** If you start a thread, provide some global flag the thread checks, and a UI button to set that flag (like stop early). If using async `background_tasks`, it might return a task object you can cancel. Ensure to handle cleanup.

The NiceGUI documentation explicitly encourages using background tasks for CPU-intensive work so the UI stays responsive. Following that guidance is important for an engineering-grade app.

Having covered events and tasks, our next focus will be specific advanced UI elements (data tables and charts) which often involve both complex components and dynamic updates.

## 6. Displaying Data: Tables and Charts

Data presentation is a common requirement – whether it’s tabular data (like configurations, results, or lists of jobs) or charts showing performance metrics. NiceGUI provides solutions for both simple and advanced use cases, including integration with powerful JS libraries.

### 6.1 Data Tables (`ui.table` and AG Grid)

For displaying data in tables, you have two main options in NiceGUI:

*   **Basic Table (`ui.table`):** This is a simple table component based on Quasar’s QTable. It’s great for moderate amounts of data and when you want quick display without heavy interactions. You provide a list of column definitions and a list of row records, and NiceGUI will render a table.
    *   **Usage:**
        ```python
        columns = [
            {"name": "name", "label": "Name", "field": "name"}, 
            {"name": "age", "label": "Age", "field": "age"}
        ]
        rows = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 21},
            {"name": "Carol", "age": 27},
        ]
        ui.table(columns=columns, rows=rows, row_key='name')
        ```
        In this example, each column dict has a `name` (key), a `label` (header text), and `field` which indicates which field in the row dict to display. `row_key='name'` tells the table which field is a unique key for each row (useful for selection or updates). If you omit `columns`, NiceGUI can infer them from the first row’s keys.
    *   **Features:** QTable (and thus `ui.table`) supports things like sorting, filtering, pagination, selection, etc., but some of these might need enabling via props. For example, to allow selection of rows, you might specify `selection='multiple'` or `selection='single'` in `ui.table` parameters. For filtering, you could bind an input to the table’s filter property.
    *   **Updating Table Data:** If the underlying `rows` data changes, you need to update the table. You could either replace the whole `rows` list and call `table.update()` or if small changes, possibly use `table.add_row({...})` or similar if provided. There is a mention of `clear()` method in an issue, implying you can clear and re-populate. For simplicity, you might just do:
        ```python
        table.rows = new_rows_list
        table.update()
        ```
        to refresh the table with new data (for example, refreshing every few seconds or after an operation).
    *   **HTML Content in Cells:** If you want to put custom HTML (links, buttons) inside table cells, there may be a way via slots or by pre-formatting the cell value as HTML. A reddit post hinted at an `html_columns` property historically. Currently, one would use Quasar's slots with NiceGUI by nesting elements using context. E.g.,
        ```python
        with ui.table(...) as table:
            with table.add_slot('body-cell-name'):  # pseudo-code for adding slot content for 'name' column cells
                ui.link(..., bind_text='name', bind_href='link_field')
        ```
        – This is advanced, but the idea is you can embed NiceGUI elements into table cells via slots. Check NiceGUI docs for the exact syntax (`ui.table(...).add_slot(...)` etc.).
    *   **When to use:** Use `ui.table` when you have a reasonably sized dataset (hundreds or a couple thousand rows maybe) and need basic display. It’s quick to set up and lightweight.

*   **Advanced Grid (`ui.aggrid`):** NiceGUI includes an integration with AG Grid, which is a powerful datagrid component for the web. This is for heavy-duty tables: large data, lots of features (sorting, filtering, grouping, editing, etc.). The NiceGUI element is `ui.aggrid(config_dict)` where you pass an AG Grid configuration (column definitions, grid options, row data, etc.).
    *   **Usage:** AG Grid expects a JS configuration object. In Python, you provide an equivalent dict. For example:
        ```python
        grid_options = {
            "columnDefs": [
                {"headerName": "Name", "field": "name", "sortable": True, "filter": True},
                {"headerName": "Age", "field": "age", "sortable": True, "filter": "agNumberColumnFilter"},
            ],
            "rowData": [
                {"name": "Alice", "age": 30}, {"name": "Bob", "age": 21}, {"name": "Carol", "age": 27},
            ],
            # ... other AG Grid options ...
        }
        grid = ui.aggrid(grid_options)
        ```
        This will render an AG Grid with those columns and data. AG Grid brings a lot: you get sorting by clicking headers, filtering (text filter or number filter as specified), and the ability to scroll through many rows efficiently (virtual DOM for performance).
    *   **Interacting with AG Grid:** The NiceGUI wrapper provides methods like `grid.run_grid_method("selectAll")` or `grid.run_row_method(row_id, 'setDataValue', col, value)` to manipulate the grid from Python. For instance, you could programmatically update a cell’s value or select a row. The GitHub issue mentions using `grid.run_row_method('Alice', 'setDataValue', 'age', 99)` to set Alice’s age to 99 in the UI. The first argument in `run_row_method` might be the row key (if defined) or some row identifier.
    *   **Events from AG Grid:** If the user edits a cell or selects a row, you’d want to catch that in Python. NiceGUI likely emits events for certain actions (maybe `on_selection_change`, `on_cell_edit` etc.). Look up if `ui.aggrid` has callback params. If not, one workaround is to have an invisible `ui.button` and use AG Grid’s callback to call a NiceGUI endpoint (this would be hacky; likely NiceGUI has direct event support though).
    *   **Performance:** AG Grid can handle thousands of rows and has features like pagination, lazy-loading, etc., which `ui.table` might not handle as well. However, using AG Grid means loading a larger JS library in the browser. NiceGUI likely includes AG Grid’s community edition by default (unless it loads on demand).
    *   **When to use:** If your app needs complex table behavior (editing cells, reordering columns, large data sets, exporting to CSV, etc.), AG Grid is the way to go. It’s an industry-grade grid component. For a simpler case, `ui.table` is easier.

In our LLM fine-tuning app context, possible uses:
*   Show a table of past fine-tuning jobs with columns like job name, status, accuracy, etc. If we want to allow sorting by accuracy or filtering by status, `ui.table` could do it, but AG Grid might give filter dropdowns out of the box.
*   If we have a table of data samples or predictions, AG Grid’s rich features might help (especially if allowing user to edit or tag data in a grid).

Remember, if using AG Grid, you’ll likely spend more time configuring it (via `columnDefs` and `grid options`). The NiceGUI documentation for `ui.aggrid` can guide what’s supported. It’s an advanced feature but good to know it’s there.

### 6.2 Charts and Graphs

NiceGUI supports plotting in multiple ways:

*   **Matplotlib Integration (`ui.pyplot` / `ui.line_plot`):** NiceGUI can directly render Matplotlib figures in the browser. If you create a `matplotlib.pyplot` figure, you can display it with `ui.pyplot(fig)` or by using `ui.line_plot` utility. In fact, NiceGUI will import Matplotlib by default (to support this) unless you disable it for performance. For instance:
    ```python
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.plot([1,2,3], [4,1,9])
    ui.pyplot(fig)
    ```
    This would show a static image of the plot. If you update the figure later, you’d re-render or update the component. The environment variable `MATPLOTLIB=false` can prevent the import if you don’t use it (to save startup time). Also, NiceGUI has `ui.line_plot` and `ui.plot` shortcuts – perhaps `ui.line_plot([y_values])` quickly plots a line chart without you dealing with Matplotlib. Check docs for these high-level methods.

*   **Third-Party JS Charts (Highcharts via plugin):** For interactive charts, NiceGUI provides the Highcharts extension. As we saw, `nicegui-highcharts` can be installed to add `ui.highchart()` component. Highcharts is a powerful JavaScript chart library with many chart types (line, bar, pie, etc.) and interactive features (tooltips, zoom, etc.). Because Highcharts is not free for commercial use, it’s not bundled in NiceGUI core (hence the separate install). But it’s easy to add:
    *   **Install:** `pip install nicegui-highcharts`.
    *   **Use:** After installation, just calling `ui.highchart(options_dict)` works (NiceGUI auto-discovers the plugin and injects it into the UI namespace). For example:
        ```python
        chart = ui.highchart({
            'title': {'text': 'Training Loss'},
            'xAxis': {'categories': ['Epoch1', 'Epoch2', 'Epoch3']},
            'series': [
                {'name': 'Loss', 'data': [0.9, 0.5, 0.2]}
            ]
        })
        ```
        This will display a column or line chart (depending on default or if you add `'chart': {'type': 'line'}` in options). The `options` object is directly passed to Highcharts, so you have full control via their API.
    *   **Updating Highcharts:** The Highcharts component likely has a method to update. According to docs snippet: "Updates can be pushed to the chart by changing the options property. After data has changed, call the update method to redraw.". So you might do:
        ```python
        chart.options['series'][0]['data'] = new_data
        chart.update()
        ```
        Or something similar. Possibly `chart.push({'name':..., 'data': [...]})` if more wrappers exist.
    Highcharts supports many chart types and is well-documented on their site. It’s a good choice if you need interactive charts with zoom/pan or if you prefer its aesthetics.

*   **Other Chart Libraries:** If not using Highcharts, you could integrate others:
    *   **Plotly:** You could use Plotly by generating a plotly JSON and either use `ui.html` to embed the chart or find a NiceGUI way. Not directly integrated, but you can output a Plotly chart as HTML and display it.
    *   **Chart.js / ECharts:** Not built-in, but possible via `ui.element` injection or custom component. ECharts might have an extension, but not sure.
    *   **AG Charts:** There’s mention of AG Charts in search results (maybe part of AG Grid offering), but likely Highcharts suffices.

In our project context:
*   We might show a training loss curve after or during training. Highcharts or Matplotlib can do that. Highcharts could even animate a live update: e.g., add a point each epoch to the series (Highcharts can append points dynamically).
*   We might show a bar chart of model sizes before/after quantization, or a pie chart of dataset distribution, etc. Highcharts offers all those.
*   If simplicity is fine (no interactivity needed), using Matplotlib to quickly generate an image is okay too. But interactivity (tooltips on hover, etc.) is usually nice for user experience.

Example Highcharts usage (from docs): They gave an example of bar chart:
```python
ui.highchart({
    'chart': {'type': 'bar'},
    'xAxis': {'categories': ['A', 'B']},
    'series': [
        {'name': 'Alpha', 'data': [0.1, 0.2]},
        {'name': 'Beta', 'data': [0.3, 0.4]},
    ],
    'title': False  # no title
})
```
That would produce a simple bar chart with two categories and two series. You can imagine updating those data arrays in a callback to reflect new values.

Charts and GPU metrics: For monitoring GPU usage or training metrics over time, you could use a Highcharts line chart that updates every few seconds. Another approach: `ui.line_plot` if it exists might not be interactive but could be easier for quick usage. DataCamp’s blurb on NiceGUI mentions it works well with NumPy and Matplotlib for data science visualizations.

Finally, always remember to consider performance: sending a huge chart data frequently can be heavy. If dealing with real-time data, consider downsampling or update incrementally (add one point rather than resend the whole series).

### 6.3 Streaming Logs and Metrics in the UI

We touched on this earlier but let’s consolidate best practices for logs and system metrics display:

*   **Logs:** Use a scrolling text display. Options:
    *   `ui.label` for single line – not ideal for multiline logs.
    *   `ui.markdown` can display multiline text (just join lines with `\n`). Use a monospace font for logs by adding a CSS class (Tailwind: `.font-mono`).
    *   A better approach might be `ui.log` if existed. Not sure if NiceGUI has a dedicated log panel.
    *   Or embed a simple `<pre>` tag: `ui.html("<pre id='logbox'></pre>")` and then use JavaScript via `ui.run_javascript` to append text to that pre tag. That’s a bit hacky but would avoid resending entire log on each update. However, it's often fine to resend moderate logs periodically.
    In any case, ensure the log panel scrolls down as new lines come. You can scroll a `ui.element` by calling a method or using JS to set `scrollTop`. NiceGUI’s forum likely has hints (maybe `ui.element('logbox').execute_js('element.scrollTop = element.scrollHeight')`).

*   **Metrics:** For system metrics like CPU, memory, GPU:
    *   Use `psutil` or similar to get CPU/mem.
    *   Use NVML (via `nvidia-ml-py3` or `pynvml`) for GPU util and mem.
    *   **Displaying:**
        *   Just numeric: e.g., `ui.label(f"GPU: {util}%")` updated by timer.
        *   Visual: `ui.linear_progress(value=util/100).props('color=green')` for a bar. Or a chart plotting utilization over time.
        *   Multi-metric: maybe a small table or list (GPU util, GPU mem, CPU util, etc).

*   **Frequency:** updating every ~1 second is enough for such metrics. If multiple metrics, you can update them in one timer callback.

*   **Integrating with the rest of UI:** If logs and metrics are on the same page as some controls, you might use a `ui.column` where top part is form/buttons, and below is a `ui.tab` or segmented area with “Logs” and “Metrics” each containing the respective outputs (so users can switch views). This goes back to using tabs to organize output sections. This improves clarity rather than one giant scroll.

By using the techniques above, you can create a rich interactive interface that not only takes input but also continuously provides feedback to the user, which is crucial in long-running ML tasks.

## 7. Styling and Theming the Interface

While functionality is paramount, a clean and consistent look-and-feel is important for user experience. NiceGUI leverages Quasar and Tailwind CSS to allow extensive styling. Here’s how to customize the appearance of your app and components:

### 7.1 Using Quasar Props and Tailwind Classes

Every NiceGUI element is backed by a Quasar component. You can pass Quasar props to an element via the element’s `.props()` method. Additionally, Tailwind CSS utility classes are available through the `.classes()` method (which simply adds those classes to the component’s DOM element).

*   **Quasar Props:** These are attributes of Quasar components. For example, a `ui.button` corresponds to a Quasar `<q-btn>` which has props like `color`, `outline`, `icon`, `round`, etc. NiceGUI lets you set them:
    ```python
    ui.button("Warning", on_click=warn).props('color=orange outline')
    ```
    This makes the button orange and outlined. For a card: `ui.card().props('bordered')` could give it a border. For input: `ui.input("Name").props('filled')` to use a filled style instead of underlined. You can find all possible props in Quasar’s documentation, and apply them as a space-separated string or multiple calls (e.g., `.props('dense').props('outline')`).

    Some particularly useful props:
    *   For buttons: `color`, `outline`, `round`, `size` (e.g., `lg` for large), `icon=<name>` to set an icon on the button.
    *   For inputs: `type=<type>` (like 'password'), `clearable` (to show an X to clear), `autofocus`, `prefix/suffix` to add labels inside.
    *   For labels/text: Actually labels are basic, but you could use `.classes` for text styling.
    *   For tables: You might pass pagination props or `dense` to make rows compact.

    The Medium article explicitly noted: “Each NiceGUI element provides a `props` method whose content is passed to the Quasar component… Have a look at the Quasar documentation for all styling props. Props with a leading `:` can contain JavaScript expressions evaluated on the client.”. The last part about `:` is advanced (for example, `':disabled="someCondition"'` to dynamically disable in client, but usually you don’t need that when controlling from Python).

*   **Tailwind Classes:** Tailwind CSS offers utility classes for spacing, sizing, colors, typography, etc. NiceGUI includes Tailwind, so you can apply those classes:
    ```python
    ui.label("Important").classes('text-red-500 font-bold')
    ```
    This would make the label text red and bold. Some common classes:
    *   **Spacing:** `mt-4` (margin-top), `mb-2` (margin-bottom), `px-4` (horizontal padding), etc.
    *   **Layout:** `flex`, `justify-center`, `items-center` for flexbox centering, etc.
    *   **Sizing:** `w-full` to make an element full width of container, or `w-1/2` for half, etc.
    *   **Typography:** `text-xl`, `text-sm` for font size, `font-bold` or `font-mono`, `text-gray-700` for colors, etc.
    *   **Borders and rounding:** `border`, `border-gray-300`, `rounded` or `rounded-full` for pill shapes.
    *   **Background colors:** `bg-blue-100` for a light blue background, etc.

    Tailwind classes are very handy to do quick styling without writing custom CSS. Since Quasar components already have a base style, mixing Tailwind is fine for many tweaks (like adding margin or changing text size).

*   **Combining Props and Classes:** You can use both. For example:
    ```python
    ui.input("Search").props('outlined round').classes('w-64')
    ```
    This would give an outlined, rounded input with fixed width using Tailwind class.

*   **Icons and theming:** If you want to change the default color theme (primary, secondary colors), NiceGUI allows customizing theme colors via environment or run config. For example, `ui.run(dark=True)` toggles dark mode globally. For primary color, you might do something like `ui.config(primary_color='#...')` or set a `QUASAR_PRIMARY` environment variable (I recall reading something on that, not certain). If not, you can always style elements individually.

Note: The Medium article’s excerpt basically says you have Quasar’s full design power. Quasar’s docs are extensive; as a NiceGUI user you mostly use `.props` and `.classes` as the gateway to that.

### 7.2 Custom CSS and Themes (Dark Mode)

If the above still isn’t enough, you can inject custom CSS or HTML:

*   **Global CSS:** You could add a `<style>` tag in the page head using `ui.add_head_html('<style> ... </style>')`. This can define global CSS rules or custom classes. For example, if you want a very custom font or something across the app.

*   **Inline Styles:** Each element has `.style()` method to set raw CSS styles if needed. Usage: `.style('background-color: #f0f0f0; border-radius: 4px;')`. The delimiter for multiple styles is `;`. This is quick for one-offs but generally Tailwind covers a lot (and using `style` directly is less responsive design friendly).

*   **Dark Mode:** As mentioned, `ui.run(native=True, dark=True)` would start the app in dark theme. You can also toggle dark mode at runtime: Possibly `ui.dark_mode()` function or use `ui.html('<body class="q-dark">')` hack. But there’s likely a built-in toggle or you can bind a checkbox to switch theme.
    If your app should follow user OS theme, you might add some JS to detect and apply accordingly. But a manual toggle is simpler.
    In dark mode, Quasar components adapt automatically if they support it (which they do).

*   **Quasar Theme Colors:** Quasar allows setting a primary, secondary, accent color, etc. NiceGUI may expose that via environment variables or config. The GitHub README suggests “customize look by defining primary, secondary and accent colors”. Perhaps you can set environment variables `PRIMARY_COLOR`, etc., before running. Alternatively, at runtime maybe `ui.colors(primary='#FF0000', secondary='#00FF00')` if such function exists.
    Check NiceGUI docs for “Styling & Appearance” section for the exact method. If not found, you can embed a small CSS like:
    ```css
    :root {
      --q-primary: #FF0000;
      --q-secondary: #00FF00;
    }
    ```
    in a `<style>` tag to override Quasar’s CSS variables.

*   **Fonts:** NiceGUI by default might use Quasar’s Roboto or so. If you want a custom font, include a link to Google Fonts via `ui.add_head_html('<link ...>')` then override classes.

*   **Responsive design:** Tailwind classes allow responsive prefixes (`sm:`, `md:` etc). So you can do `classes('w-full md:w-1/2')` to make an element full width on small screens and half width on medium up. Use this for adapting layout on mobile vs desktop.

*   **Custom Vue Components:** For very advanced cases, NiceGUI allows embedding custom Vue components if you have some you want to use (e.g., a third-party component or one you wrote). This is beyond typical usage, but in docs index we saw mention of “Custom Vue Components”. Essentially you could register a Vue component and then use it as a NiceGUI element. Most likely not needed for us, since NiceGUI + Quasar + plugins cover most needs.

*   **Example – applying styles:** Suppose we want our “Start Fine-Tuning” button to stand out as a primary action:
    ```python
    start_btn = ui.button("🚀 Start Fine-Tuning").props('unelevated color=primary')
    ```
    Here, `unelevated` makes it a flat button (filled with primary color) instead of default raised. We set an emoji icon via label just as a demo. If we had set a custom primary color theme, it will use that color for the button background. If not, Quasar’s default blue will be used (unless we specify `color` explicitly as we did).

    Another example: we want the logs area to be a scrolling box of fixed height, with monospaced font:
    ```python
    log_container = ui.element('div').style('max-height: 200px; overflow:auto;')
    log_text = ui.markdown('', on_render=None)  # an empty markdown we’ll fill
    log_container.add(log_text)
    log_text.classes('font-mono text-sm')
    ```
    Here, we manually created a `<div>` using `ui.element('div')` (a generic element), applied a max-height and scrollbar via CSS, and put a markdown inside it with monospaced small text. We would then update `log_text.content` with log lines. This is a way to achieve scrollable text if no built-in component does it.

Styling can be iterative – start with basic, then refine. The key is knowing that `.props()`, `.classes()`, and `.style()` give you full control.

As a final note, consistency matters: decide on a color scheme and apply it to related components. Use spacing systematically (Tailwind makes that easier). And test both in light and dark modes if you intend to support both.

## 8. Deployment and Configuration

Once your NiceGUI app is developed, you need to run it reliably in your target environment. Deployment may involve containerization (Docker), environment variable configurations, and possibly running in a desktop context if needed. This section covers how to configure NiceGUI and deploy it.

### 8.1 Running in Development vs. Production

During development, you typically run `ui.run()` in your script which starts a web server on port 8080 (by default) and opens a browser window (unless `ui.run()` is called with `shutdown_trigger=None` to not auto-open). Key differences between dev and production:

*   **Auto-reload:** In dev, NiceGUI auto-reloads on code changes. This is convenient but in production you’ll want to disable that. Usually, `ui.run(reload=False)` or simply not using the dev server's reload.
*   **Host and Port:** By default, host is `localhost`. To allow external access (in a container or network), you might set `ui.run(host='0.0.0.0', port=8080)`. In production behind a proxy, you might run on a different port or interface accordingly.
*   **Logging:** NiceGUI will show logs via Uvicorn. For production, you might want to tweak log level or format. You can configure FastAPI/Uvicorn logger via environment or programmatically if needed.
*   **Process management:** In dev you just `Ctrl+C` to stop. In production, you’d run this via a process manager (systemd, docker, etc.) to ensure it stays running.

No special “production mode” flag is needed beyond that; just ensure debug modes are off if any (FastAPI debug, etc., but I think NiceGUI doesn’t expose that as separate concept since it’s mostly UI code).

### 8.2 Docker Deployment

Docker is an excellent way to ship the app. There are two approaches:

*   **Using the official NiceGUI image as base:** The image `zauberzeug/nicegui` (on Docker Hub) is essentially an environment with NiceGUI installed. You can use it to run your app by mounting your code or building on top of it.
    *   **Example Dockerfile:**
        ```dockerfile
        FROM zauberzeug/nicegui:latest
        COPY ./my_app /app
        CMD ["python", "main.py"]
        ```
        This assumes your app code is in `my_app` directory and `main.py` launches the ui.
    *   The official image likely uses `python main.py` by default if you run it with your code mounted at `/app`. The README suggests you can do `docker run -p 8080:8080 zauberzeug/nicegui` to run their docs app.
    *   Ensure you expose the correct port (8080 by default) in Docker.
    *   You might want a specific tag for NiceGUI version, e.g., `zauberzeug/nicegui:3.2.0` for a known version (since `latest` can update).

*   **Custom image from scratch:** If you prefer, you can start from a Python base image and `pip install nicegui` (and any other dependencies like your ML libraries):
    *   **Example:**
        ```dockerfile
        FROM python:3.10-slim
        WORKDIR /app
        # Install system dependencies if needed (for example, if using GPU or specific libs)
        # e.g., RUN apt-get update && apt-get install -y some-lib
        COPY requirements.txt .
        RUN pip install -r requirements.txt  # this includes nicegui
        COPY . .
        EXPOSE 8080
        CMD ["python", "main.py"]
        ```
        This way, you have more control. The trade-off is you have to ensure all needed libs (like possibly system packages for NVIDIA if doing GPU stuff, etc.) are included.

*   **GPU Support in Docker:** If your fine-tuning uses GPU (via PyTorch or TensorFlow), you’d need to base on a CUDA image or use nvidia’s base images and install nicegui there. That goes beyond NiceGUI itself but important for such an app.
    *   For instance, start from `nvidia/cuda:XX.YY-base` and then install Python and libs, or use a prebuilt DL image from PyTorch or TF that has CUDA and then `pip install nicegui`.
    *   Use `--gpus all` when running docker to pass GPUs.

*   **Environment Variables for Config:** NiceGUI respects some env vars:
    *   `PORT`: It will use this as default port if set (common in Heroku, etc. – ensure to override NiceGUI’s default). One GitHub issue indicated that `PORT` env could be overridden by nicegui if not careful, but presumably if you call `ui.run(port=os.getenv("PORT", 8080))` you handle it.
    *   `HOST`: similar for host.
    *   `MATPLOTLIB`: as mentioned, set `MATPLOTLIB=false` to skip matplotlib import if not needed.
    *   Possibly `NICEGUI_HEADLESS`: not sure if exists, but maybe to run without launching a browser even if `ui.run(..., native=True)`? But since in Docker there's no display, it will anyway not do GUI.

*   **Reverse Proxy / HTTPS:** In production, often you put Nginx or similar in front. NiceGUI is just a web server – treat it like any FastAPI app. That means:
    *   Use `host=0.0.0.0` to listen to all interfaces (or specific if needed).
    *   Proxy websockets correctly (if using Nginx, ensure upgrade headers etc. for socket.io).
    *   If you need SSL, either terminate at proxy or use a certificate at the app (maybe simpler to do at proxy).
    *   If behind a proxy that handles paths, you might mount NiceGUI at a subpath – not sure if straightforward, likely you’d handle it at routing or in the proxy config.

*   **Scaling:** Since NiceGUI is one process, scaling horizontally means multiple container instances and some form of load balancing. But given it’s stateful (each session sticks to one backend unless you share state in a DB), sticky sessions would be needed if behind a load balancer. For our use-case, probably one instance is fine (or at most manually handle distribution of jobs).

*   **Running as service:** If not using Docker, you can still run behind `uvicorn`/`gunicorn`. For example, run `uvicorn main:app --workers 1` (though multiple workers not supported due to single state, so keep 1). Actually NiceGUI’s `ui.run()` probably uses uvicorn internally. If you needed to integrate into a larger FastAPI app, you can mount or include NiceGUI’s app (the GitHub comment suggests you can use NiceGUI with an existing FastAPI router).

### 8.3 Environment Variables and Config Options

We’ve mentioned a few environment variables. Let’s list the notable ones for NiceGUI configuration:

*   `HOST` / `PORT`: control network binding if not specified in code. Often used in hosting services. If using `ui.run()`, you can just specify these in code from `os.environ`.
*   `MATPLOTLIB`: default “true”. If set to “false”, NiceGUI will not import matplotlib on startup. This is good if you don’t use any plotting features from it, saving memory and time.
*   `NICEGUI_HOME`: Possibly where NiceGUI stores something (not sure if it stores anything like persistence or user uploads).
*   `DEBUG`: Not sure if NiceGUI uses this, but FastAPI uses `app.debug`. There might be a `ui.run(debug=True/False)`.
*   `UVICORN_RELOAD`: If you run in a container with reload, but usually in prod you wouldn’t.

Additionally, NiceGUI’s `ui.run()` has parameters:
*   `title="Your App"` – sets the page title (the `<title>` tag).
*   `favicon="path_or_emoji"` – you can set a favicon (they even allow emoji or base64).
*   `native=True` – runs in native (desktop window) mode if PyWebview is installed.
*   `reload=False` – to disable the auto-reloader.
*   `port`, `host` – as described.
*   `socketio_trace=True/False` – maybe to enable verbose logging of socket events for debug.
*   Possibly `autoreload_dir` – if you want to watch additional dirs for changes.

**Configuration & Deployment Reference:** The search snippet references “Configuration & Deployment” docs where some of these are detailed. It likely lists env vars and `ui.run` args.

### 8.4 Native Desktop Mode

One standout feature: NiceGUI can open a native window (using an embedded browser via PyWebview). This is akin to an Electron app, meaning you can distribute your app as a desktop application. Key points:

*   To use native mode, you need to `pip install pywebview` (NiceGUI will detect it). If not installed, `ui.run(native=True)` will prompt an error or suggestion to install `pywebview`.
*   When you do `ui.run(native=True)`, instead of opening the system default browser, it opens a desktop window containing the app. This is great for kiosk or end-users who expect a desktop program.
*   On Ubuntu or some Linux, you might need additional packages for Webview (like `webkitgtk`). On Windows/Mac, PyWebview uses built-in WebView components.
*   **Packaging:** You can bundle this into an executable using PyInstaller or similar. The NiceGUI team mentioned packaging as standalone is possible.
*   **Features in native mode:** You can customize the window (size, fullscreen, frameless, etc., likely via parameters to `ui.run` such as `width=...`, `height=...` or through environment). Possibly in docs: “To customize the initial window size and display mode, use the window ...” was hinted (maybe they allow `ui.run(native=True, width=800, height=600, fullscreen=False)` etc).
*   You can still access the app via browser at the same time if you go to `localhost:8080` (unless you specifically restrict it).
*   **Use cases:** If you want to provide this tool to someone non-technical, you could give them an executable that opens with a nice GUI window, so they don’t even realize it’s a web app.

Given our focus is likely on a web interface in a server environment (for multiple users perhaps), native mode is optional. But it’s good to mention for completeness since the user asked for all aspects (and the link referenced an Electron-like capability).

In summary:
*   For server deployment, Docker on a server with host networking or behind proxy is typical.
*   For a desktop app, use native mode and consider packaging.

One more thing: **Persistent storage** – if your app needs to save settings or data, you’ll do that in files or a database as usual. NiceGUI provides a simple built-in “storage” that persists across sessions (maybe using SQLite or JSON). The docs mention “easy-to-use per-user and general persistence”. That suggests something like:
```python
ui.client.storage.user.put("pref", value)
value = ui.client.storage.user.get("pref")
```
But I'm not certain of API. Possibly they just mean using browser localStorage or cookies via their API. If relevant, check “Storage | NiceGUI” (which appeared in search results) – likely they have 5 built-in storage types (maybe memory, sqlite, redis, etc.). If your project needs user preferences saved, consider exploring that.

## 9. Best Practices and Project Architecture

To ensure your NiceGUI application is maintainable and robust, consider the following best practices in structuring the code and handling common scenarios:

### 9.1 Code Organization and Modularization

Modular code is easier to navigate and update. Rather than one huge `main.py`, split your app into logical components:

*   **Pages as Separate Modules:** If you have multiple pages (using `@ui.page`), you can define each in its own file. For example, `pages/home.py` with a `home_page()` function decorated with `@ui.page('/')`, `pages/monitor.py` for the monitor page, etc. In `main.py`, you would import these modules so that the page routes get registered. This keeps each page’s UI definition isolated.

*   **Reusable Components:** If certain UI parts are used in multiple places, make a function or class for them. For instance, if you have a panel that displays GPU stats, you can implement `components/gpu_panel.py` with a function `create_gpu_panel()` that returns a container or dictionary of UI elements. Then any page can call that to insert a GPU panel. This avoids duplicating UI code.

*   **State Management:** Consider using classes or data structures to hold state. For example, define a `JobManager` class that keeps track of running fine-tuning jobs, their parameters, progress, etc., with methods to start/cancel jobs. This object can be imported where needed (since NiceGUI is single-process, a global object works). The UI callbacks then call methods on this manager rather than fiddling with global dictionaries directly. This adds structure and makes testing easier.

*   **Avoiding Circular Imports:** If splitting pages, be careful that they might import common components or state. Use a central module (like an `app_state.py`) for shared objects rather than cross-importing pages.

*   **File structure example:**
    ```
    my_app/
      main.py            # starts ui.run, imports pages
      pages/
         __init__.py
         home.py
         configure.py
         monitor.py
         results.py
      components/
         __init__.py
         job_table.py
         charts.py
         gpu_panel.py
      services/
         jobs.py         # job management logic (starting threads, etc.)
         metrics.py      # e.g., functions to fetch system metrics
      static/            # static files if any (images, etc.)
    ```
    The NiceGUI template likely uses a similar structure, and even includes directories for tests, config, etc. Adapt as needed.

*   **Naming Conventions:** Name UI element variables clearly, e.g. `start_button`, `status_label`, so that in callbacks you know what they refer to. This is trivial but helps when code grows.

*   **Comments and Docstrings:** Document tricky parts, like `# This timer updates the log output from background thread`. Remember an AI agent or another engineer might read this and benefit from context.

### 9.2 Avoiding Common Pitfalls (Blocking, etc.)

Some pitfalls to watch out for:

*   **Blocking the UI thread:** As emphasized, do not perform heavy computations or blocking I/O in event callbacks without offloading. If you call a slow function in a button `on_click`, the UI (and all clients) will freeze until it finishes. Always move such work to a background task or thread. Use `async` where possible (e.g., use `await asyncio.sleep` instead of `time.sleep`, because `time.sleep` blocks, whereas `await asyncio.sleep` yields control back to server).

*   **Thread Safety:** If you do use threads, be careful when they interact with shared data. Protect with locks if multiple threads write to the same list/dict. Also, as noted, avoid directly manipulating NiceGUI UI elements from background threads. Instead, use a safe pattern (like set a flag and let main thread’s timer or next callback update the UI). If you must update from a thread, ensure the NiceGUI docs say it’s allowed or not. (Often UI libs are single-threaded; NiceGUI likely is too.)

*   **Large Data in UI:** Sending very large data via the WebSocket (like a huge image or a million rows table) can be slow or crash the browser. For images, consider resizing or compressing. For tables, use pagination or AG Grid’s virtualization. For charts, limit data points or decimate if too dense.

*   **Memory Management:** If you display a lot of images or plots, clean them up if not needed. For example, if you keep updating a Matplotlib figure and not using the old ones, ensure references are dropped so Python can GC them. In the browser, if you add elements dynamically without removing old ones, you could inflate memory. Use `.delete()` on NiceGUI elements if available (maybe `element.remove()` or simply design so that you update existing components instead of creating new ones repeatedly).

*   **Session Management:** If multi-user, be mindful of global state. For example, if you have a global list of jobs, prefix entries by user or keep separate structures per user. NiceGUI might allow per-session data via something like `ui.get_client().storage` etc. If one user’s action should not affect others, isolate it. Conversely, if it should (like a shared dashboard), handle concurrency (two users starting jobs at same time altering same global list – use locks).

*   **Clean Shutdown:** If your app spawns threads or subprocesses, handle termination. When NiceGUI exits (perhaps user closes window or you hit `Ctrl+C` on server), your threads might still run unless daemonized. Mark threads as daemon or catch the termination signal to instruct them to stop gracefully. This prevents orphan processes.

*   **Security:** NiceGUI doesn’t inherently have auth or permission checks. If your app will be deployed on a server accessible by many, consider adding a login page or at least basic HTTP auth in front (perhaps using FastAPI dependencies or an auth proxy). Also validate user inputs (though being a mostly controlled interface, risk is low, but e.g., if a user can input a shell command to run, that’s dangerous – apply typical security measures).

*   **Testing:** While we postpone heavy testing discussions, note that NiceGUI includes a pytest plugin for UI tests. You can write tests that spin up the UI and use Playwright to simulate clicks. This is advanced, but if building a serious app, writing some tests for critical UI flows is beneficial. The NiceGUI template’s inclusion of test tools hints at this.

### 9.3 Extending NiceGUI (Plugins and Custom Components)

We already saw one extension: `nicegui-highcharts`. There could be others and you can create your own:

*   **Community Extensions:** Check NiceGUI GitHub or community for plugins like `nicegui-template` (for project scaffolding), maybe a `nicegui-<something>` for other JS libs or integrations (for example, maybe someone made `nicegui-d3` or `nicegui-leaflet` for maps, etc.). The installation and usage pattern likely similar to highcharts: install package, import or just call component after installation.

*   **ROSYS Integration:** The template mentioned an option `use_rosys`. RoSys is a robotics framework by Zauberzeug. If that’s enabled, it likely pulls in some components or logic for robotics. Not relevant to our case, but worth noting if doing robotics UI, they have synergy.

*   **Custom Vue Component:** If you have a specific front-end widget that NiceGUI doesn’t support, you can integrate it. The docs mention the ability to register custom components (maybe using `ui.add_component('tag-name', VueComponent)` or an API to define a Python wrapper for a JS component). For example, if you wanted to use a particular JS chart library that’s not available, you could manually include its JS file (via `ui.add_head_html(<script> tag)`) and then use `ui.element('custom-tag')` with appropriate props to instantiate it. For two-way communication, you might need to tap into NiceGUI’s socket events. This is advanced and usually not needed because NiceGUI plus Quasar covers a lot.

*   **Contributing to NiceGUI:** If you find a missing feature that would benefit others, consider contributing upstream. The maintainers seem active and welcoming to suggestions (their discussions indicate they continuously improve docs and features).

*   **Performance tuning:** If you eventually want to scale up, consider where bottlenecks might be: heavy computations (move to background or external service), large data through WebSocket (maybe compress or send diff updates), number of concurrent clients (one process can handle many async users if not CPU-bound, but if needed, run multiple instances behind a load balancer with session stickiness).

By adhering to these best practices, your NiceGUI application will be easier to maintain and extend. The goal is to structure it in a way that the UI code is clean and the backend logic (like starting jobs, reading metrics) is separated so it could even be reused or tested independently.

## 10. Summary and Next Steps

In this engineer’s handbook, we’ve covered the full landscape of developing a web application with NiceGUI, from initial setup to deployment. To recap the key points:

*   **NiceGUI Overview:** It’s a Python-first web UI framework combining FastAPI on the back and Vue/Quasar on the front, allowing rapid development of browser-based GUIs with rich components. We discussed how its backend-driven model simplifies state handling compared to JavaScript-heavy approaches.

*   **Setup and Structure:** We walked through installing NiceGUI (via `pip` or Docker) and using the official template to scaffold a project. A well-structured project might separate pages and components into modules, which is crucial as the app grows.

*   **UI Development:** NiceGUI offers a wide range of components – we went over basic elements (labels, inputs, buttons) and more advanced ones (dialogs, menus, tables, charts). You learned how to organize these with layout containers (rows, columns, cards) to create a responsive interface. We emphasized the convenience of NiceGUI’s context management (`with ui.row(): ...`) which makes the code mirror the UI hierarchy.

*   **Interactivity and State:** Handling user events in NiceGUI is straightforward – callbacks in Python for clicks and changes. For dynamic behavior, we covered data binding to automatically sync UI with state, and the use of `ui.timer` for periodic updates (like updating metrics displays). Long-running tasks should be offloaded to background threads or async tasks to keep the UI responsive. We gave patterns for updating the UI from such tasks (e.g., using shared variables and timers to bridge threads).

*   **Data Presentation:** For tables, use `ui.table` for simpler needs or `ui.aggrid` for heavy-duty interactive grids. For visualization, leverage `ui.pyplot` for quick Matplotlib plots or integrate Highcharts via `nicegui-highcharts` for interactive charts. These tools allow you to provide real-time feedback (training progress charts, log outputs, etc.) in your ML app’s interface.

*   **Styling and Theming:** NiceGUI’s integration with Quasar and Tailwind gives you fine control over aesthetics. Use `.props()` to set component styles and `.classes()` for quick CSS utility classes. We discussed enabling dark mode and customizing theme colors to match your project’s branding. This ensures your app not only functions well but also looks polished.

*   **Deployment:** We reviewed deploying NiceGUI apps in Docker – mapping ports and using the official image or a custom build. Configuration options like `host`, `port`, and the ability to enable native desktop mode (with `ui.run(native=True)`) provide flexibility in how you deliver your app. Whether it’s running on a cloud server with Docker or packaged as a desktop tool, NiceGUI can accommodate it.

*   **Best Practices:** Finally, we compiled best practices such as modularizing code, avoiding blocking operations, ensuring thread safety, and leveraging NiceGUI’s features for persistence or testing. These guidelines will help keep the project maintainable as it evolves. We also noted how to extend functionality via plugins or custom components if needed.

**Next Steps:** With this comprehensive guide, you are well-equipped to build your application’s UI using NiceGUI. A sensible next step is to initialize a project (using the template or manually), outline your pages (perhaps a main dashboard, a configuration page, a monitoring page as identified), and implement a prototype of each key feature using the patterns here. Test the interactions (e.g., start a dummy long task and see if the UI remains responsive with a timer updating progress).

As you start integrating the actual ML quantization/fine-tuning logic, refer back to relevant sections: for example, Events and State Management when hooking up the “Start Fine-Tuning” button to launch the process, or Displaying Data when showing training metrics. Keep in mind the separation of concerns – the UI should trigger backend functions (which you write or import) and display results, but the heavy ML lifting happens in those backend functions (possibly in a thread or separate process). This division will make both development and debugging easier.

Lastly, make use of NiceGUI’s official documentation and community (the subreddit / Discord) for any nuanced questions. The creators of NiceGUI actively engage with the community, as evidenced by their frequent improvements and responsiveness to issues. If something isn’t working as expected or you need a feature, you might find that others have asked similar questions (and the answers could be in those discussions).

By following this handbook and iterating on your design, you’ll develop a robust web application interface for your ML tasks that avoids guesswork and adheres to proven patterns. Happy coding with NiceGUI! Good luck with your project, and enjoy the process of building a nice GUI – the nice way 😉.

---

## Sources:

*   NiceGUI GitHub README (features, usage)
*   NiceGUI SourceForge Summary (overview of capabilities)
*   NiceGUI Highcharts Documentation (usage example)
*   NiceGUI Template Documentation (project setup and options)
*   Medium Article on NiceGUI vs others (data binding, customization)
*   Reddit Q&A and Announcements (native mode, deployment tips)
