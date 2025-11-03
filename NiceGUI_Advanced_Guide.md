# NiceGUI Engineer's Handbook - Part 2: Advanced Guide

## Introduction

This is Part 2 of the NiceGUI Engineer's Handbook, covering advanced topics for building production-ready web applications with NiceGUI. Part 1 (Core Concepts) covered the fundamentals: setup, UI components, layouts, and basic event handling. In this part, we'll explore more sophisticated features including data visualization with tables and charts, styling and theming, deployment strategies, and best practices for maintaining a robust codebase.

If you haven't read Part 1, we recommend starting there to understand the foundational concepts of NiceGUI's backend-first architecture, auto-context system, and page routing.

## Table of Contents

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

## 6. Displaying Data: Tables and Charts

Data presentation is a common requirement – whether it's tabular data (like configurations, results, or lists of jobs) or charts showing performance metrics. NiceGUI provides solutions for both simple and advanced use cases, including integration with powerful JS libraries.

### 6.1 Data Tables (`ui.table` and AG Grid)

For displaying data in tables, you have two main options in NiceGUI:

*   **Basic Table (`ui.table`):** This is a simple table component based on Quasar's QTable. It's great for moderate amounts of data and when you want quick display without heavy interactions. You provide a list of column definitions and a list of row records, and NiceGUI will render a table.
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
        In this example, each column dict has a `name` (key), a `label` (header text), and `field` which indicates which field in the row dict to display. `row_key='name'` tells the table which field is a unique key for each row (useful for selection or updates). If you omit `columns`, NiceGUI can infer them from the first row's keys.
    *   **Features:** QTable (and thus `ui.table`) supports things like sorting, filtering, pagination, selection, etc., but some of these might need enabling via props. For example, to allow selection of rows, you might specify `selection='multiple'` or `selection='single'` in `ui.table` parameters. For filtering, you could bind an input to the table's filter property.
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
    *   **When to use:** Use `ui.table` when you have a reasonably sized dataset (hundreds or a couple thousand rows maybe) and need basic display. It's quick to set up and lightweight.

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
    *   **Interacting with AG Grid:** The NiceGUI wrapper provides methods like `grid.run_grid_method("selectAll")` or `grid.run_row_method(row_id, 'setDataValue', col, value)` to manipulate the grid from Python. For instance, you could programmatically update a cell's value or select a row. The GitHub issue mentions using `grid.run_row_method('Alice', 'setDataValue', 'age', 99)` to set Alice's age to 99 in the UI. The first argument in `run_row_method` might be the row key (if defined) or some row identifier.
    *   **Events from AG Grid:** If the user edits a cell or selects a row, you'd want to catch that in Python. NiceGUI likely emits events for certain actions (maybe `on_selection_change`, `on_cell_edit` etc.). Look up if `ui.aggrid` has callback params. If not, one workaround is to have an invisible `ui.button` and use AG Grid's callback to call a NiceGUI endpoint (this would be hacky; likely NiceGUI has direct event support though).
    *   **Performance:** AG Grid can handle thousands of rows and has features like pagination, lazy-loading, etc., which `ui.table` might not handle as well. However, using AG Grid means loading a larger JS library in the browser. NiceGUI likely includes AG Grid's community edition by default (unless it loads on demand).
    *   **When to use:** If your app needs complex table behavior (editing cells, reordering columns, large data sets, exporting to CSV, etc.), AG Grid is the way to go. It's an industry-grade grid component. For a simpler case, `ui.table` is easier.

In our LLM fine-tuning app context, possible uses:
*   Show a table of past fine-tuning jobs with columns like job name, status, accuracy, etc. If we want to allow sorting by accuracy or filtering by status, `ui.table` could do it, but AG Grid might give filter dropdowns out of the box.
*   If we have a table of data samples or predictions, AG Grid's rich features might help (especially if allowing user to edit or tag data in a grid).

Remember, if using AG Grid, you'll likely spend more time configuring it (via `columnDefs` and `grid options`). The NiceGUI documentation for `ui.aggrid` can guide what's supported. It's an advanced feature but good to know it's there.

### 6.2 Charts and Graphs

NiceGUI supports plotting in multiple ways:

*   **Matplotlib Integration (`ui.pyplot` / `ui.line_plot`):** NiceGUI can directly render Matplotlib figures in the browser. If you create a `matplotlib.pyplot` figure, you can display it with `ui.pyplot(fig)` or by using `ui.line_plot` utility. In fact, NiceGUI will import Matplotlib by default (to support this) unless you disable it for performance. For instance:
    ```python
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.plot([1,2,3], [4,1,9])
    ui.pyplot(fig)
    ```
    This would show a static image of the plot. If you update the figure later, you'd re-render or update the component. The environment variable `MATPLOTLIB=false` can prevent the import if you don't use it (to save startup time). Also, NiceGUI has `ui.line_plot` and `ui.plot` shortcuts – perhaps `ui.line_plot([y_values])` quickly plots a line chart without you dealing with Matplotlib. Check docs for these high-level methods.

*   **Third-Party JS Charts (Highcharts via plugin):** For interactive charts, NiceGUI provides the Highcharts extension. As we saw, `nicegui-highcharts` can be installed to add `ui.highchart()` component. Highcharts is a powerful JavaScript chart library with many chart types (line, bar, pie, etc.) and interactive features (tooltips, zoom, etc.). Because Highcharts is not free for commercial use, it's not bundled in NiceGUI core (hence the separate install). But it's easy to add:
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
    Highcharts supports many chart types and is well-documented on their site. It's a good choice if you need interactive charts with zoom/pan or if you prefer its aesthetics.

*   **Other Chart Libraries:** If not using Highcharts, you could integrate others:
    *   **Plotly:** You could use Plotly by generating a plotly JSON and either use `ui.html` to embed the chart or find a NiceGUI way. Not directly integrated, but you can output a Plotly chart as HTML and display it.
    *   **Chart.js / ECharts:** Not built-in, but possible via `ui.element` injection or custom component. ECharts might have an extension, but not sure.
    *   **AG Charts:** There's mention of AG Charts in search results (maybe part of AG Grid offering), but likely Highcharts suffices.

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

Charts and GPU metrics: For monitoring GPU usage or training metrics over time, you could use a Highcharts line chart that updates every few seconds. Another approach: `ui.line_plot` if it exists might not be interactive but could be easier for quick usage. DataCamp's blurb on NiceGUI mentions it works well with NumPy and Matplotlib for data science visualizations.

Finally, always remember to consider performance: sending a huge chart data frequently can be heavy. If dealing with real-time data, consider downsampling or update incrementally (add one point rather than resend the whole series).

### 6.3 Streaming Logs and Metrics in the UI

We touched on this earlier but let's consolidate best practices for logs and system metrics display:

*   **Logs:** Use a scrolling text display. Options:
    *   `ui.label` for single line – not ideal for multiline logs.
    *   `ui.markdown` can display multiline text (just join lines with `\n`). Use a monospace font for logs by adding a CSS class (Tailwind: `.font-mono`).
    *   A better approach might be `ui.log` if existed. Not sure if NiceGUI has a dedicated log panel.
    *   Or embed a simple `<pre>` tag: `ui.html("<pre id='logbox'></pre>")` and then use JavaScript via `ui.run_javascript` to append text to that pre tag. That's a bit hacky but would avoid resending entire log on each update. However, it's often fine to resend moderate logs periodically.
    In any case, ensure the log panel scrolls down as new lines come. You can scroll a `ui.element` by calling a method or using JS to set `scrollTop`. NiceGUI's forum likely has hints (maybe `ui.element('logbox').execute_js('element.scrollTop = element.scrollHeight')`).

*   **Metrics:** For system metrics like CPU, memory, GPU:
    *   Use `psutil` or similar to get CPU/mem.
    *   Use NVML (via `nvidia-ml-py3` or `pynvml`) for GPU util and mem.
    *   **Displaying:**
        *   Just numeric: e.g., `ui.label(f"GPU: {util}%")` updated by timer.
        *   Visual: `ui.linear_progress(value=util/100).props('color=green')` for a bar. Or a chart plotting utilization over time.
        *   Multi-metric: maybe a small table or list (GPU util, GPU mem, CPU util, etc).

*   **Frequency:** updating every ~1 second is enough for such metrics. If multiple metrics, you can update them in one timer callback.

*   **Integrating with the rest of UI:** If logs and metrics are on the same page as some controls, you might use a `ui.column` where top part is form/buttons, and below is a `ui.tab` or segmented area with "Logs" and "Metrics" each containing the respective outputs (so users can switch views). This goes back to using tabs to organize output sections. This improves clarity rather than one giant scroll.

By using the techniques above, you can create a rich interactive interface that not only takes input but also continuously provides feedback to the user, which is crucial in long-running ML tasks.

## 7. Styling and Theming the Interface

While functionality is paramount, a clean and consistent look-and-feel is important for user experience. NiceGUI leverages Quasar and Tailwind CSS to allow extensive styling. Here's how to customize the appearance of your app and components:

### 7.1 Using Quasar Props and Tailwind Classes

Every NiceGUI element is backed by a Quasar component. You can pass Quasar props to an element via the element's `.props()` method. Additionally, Tailwind CSS utility classes are available through the `.classes()` method (which simply adds those classes to the component's DOM element).

*   **Quasar Props:** These are attributes of Quasar components. For example, a `ui.button` corresponds to a Quasar `<q-btn>` which has props like `color`, `outline`, `icon`, `round`, etc. NiceGUI lets you set them:
    ```python
    ui.button("Warning", on_click=warn).props('color=orange outline')
    ```
    This makes the button orange and outlined. For a card: `ui.card().props('bordered')` could give it a border. For input: `ui.input("Name").props('filled')` to use a filled style instead of underlined. You can find all possible props in Quasar's documentation, and apply them as a space-separated string or multiple calls (e.g., `.props('dense').props('outline')`).

    Some particularly useful props:
    *   For buttons: `color`, `outline`, `round`, `size` (e.g., `lg` for large), `icon=<name>` to set an icon on the button.
    *   For inputs: `type=<type>` (like 'password'), `clearable` (to show an X to clear), `autofocus`, `prefix/suffix` to add labels inside.
    *   For labels/text: Actually labels are basic, but you could use `.classes` for text styling.
    *   For tables: You might pass pagination props or `dense` to make rows compact.

    The Medium article explicitly noted: "Each NiceGUI element provides a `props` method whose content is passed to the Quasar component… Have a look at the Quasar documentation for all styling props. Props with a leading `:` can contain JavaScript expressions evaluated on the client.". The last part about `:` is advanced (for example, `':disabled="someCondition"'` to dynamically disable in client, but usually you don't need that when controlling from Python).

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

Note: The Medium article's excerpt basically says you have Quasar's full design power. Quasar's docs are extensive; as a NiceGUI user you mostly use `.props` and `.classes` as the gateway to that.

### 7.2 Custom CSS and Themes (Dark Mode)

If the above still isn't enough, you can inject custom CSS or HTML:

*   **Global CSS:** You could add a `<style>` tag in the page head using `ui.add_head_html('<style> ... </style>')`. This can define global CSS rules or custom classes. For example, if you want a very custom font or something across the app.

*   **Inline Styles:** Each element has `.style()` method to set raw CSS styles if needed. Usage: `.style('background-color: #f0f0f0; border-radius: 4px;')`. The delimiter for multiple styles is `;`. This is quick for one-offs but generally Tailwind covers a lot (and using `style` directly is less responsive design friendly).

*   **Dark Mode:** As mentioned, `ui.run(native=True, dark=True)` would start the app in dark theme. You can also toggle dark mode at runtime: Possibly `ui.dark_mode()` function or use `ui.html('<body class="q-dark">')` hack. But there's likely a built-in toggle or you can bind a checkbox to switch theme.
    If your app should follow user OS theme, you might add some JS to detect and apply accordingly. But a manual toggle is simpler.
    In dark mode, Quasar components adapt automatically if they support it (which they do).

*   **Quasar Theme Colors:** Quasar allows setting a primary, secondary, accent color, etc. NiceGUI may expose that via environment variables or config. The GitHub README suggests "customize look by defining primary, secondary and accent colors". Perhaps you can set environment variables `PRIMARY_COLOR`, etc., before running. Alternatively, at runtime maybe `ui.colors(primary='#FF0000', secondary='#00FF00')` if such function exists.
    Check NiceGUI docs for "Styling & Appearance" section for the exact method. If not found, you can embed a small CSS like:
    ```css
    :root {
      --q-primary: #FF0000;
      --q-secondary: #00FF00;
    }
    ```
    in a `<style>` tag to override Quasar's CSS variables.

*   **Fonts:** NiceGUI by default might use Quasar's Roboto or so. If you want a custom font, include a link to Google Fonts via `ui.add_head_html('<link ...>')` then override classes.

*   **Responsive design:** Tailwind classes allow responsive prefixes (`sm:`, `md:` etc). So you can do `classes('w-full md:w-1/2')` to make an element full width on small screens and half width on medium up. Use this for adapting layout on mobile vs desktop.

*   **Custom Vue Components:** For very advanced cases, NiceGUI allows embedding custom Vue components if you have some you want to use (e.g., a third-party component or one you wrote). This is beyond typical usage, but in docs index we saw mention of "Custom Vue Components". Essentially you could register a Vue component and then use it as a NiceGUI element. Most likely not needed for us, since NiceGUI + Quasar + plugins cover most needs.

*   **Example – applying styles:** Suppose we want our "Start Fine-Tuning" button to stand out as a primary action:
    ```python
    start_btn = ui.button("🚀 Start Fine-Tuning").props('unelevated color=primary')
    ```
    Here, `unelevated` makes it a flat button (filled with primary color) instead of default raised. We set an emoji icon via label just as a demo. If we had set a custom primary color theme, it will use that color for the button background. If not, Quasar's default blue will be used (unless we specify `color` explicitly as we did).

    Another example: we want the logs area to be a scrolling box of fixed height, with monospaced font:
    ```python
    log_container = ui.element('div').style('max-height: 200px; overflow:auto;')
    log_text = ui.markdown('', on_render=None)  # an empty markdown we'll fill
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

*   **Auto-reload:** In dev, NiceGUI auto-reloads on code changes. This is convenient but in production you'll want to disable that. Usually, `ui.run(reload=False)` or simply not using the dev server's reload.
*   **Host and Port:** By default, host is `localhost`. To allow external access (in a container or network), you might set `ui.run(host='0.0.0.0', port=8080)`. In production behind a proxy, you might run on a different port or interface accordingly.
*   **Logging:** NiceGUI will show logs via Uvicorn. For production, you might want to tweak log level or format. You can configure FastAPI/Uvicorn logger via environment or programmatically if needed.
*   **Process management:** In dev you just `Ctrl+C` to stop. In production, you'd run this via a process manager (systemd, docker, etc.) to ensure it stays running.

No special "production mode" flag is needed beyond that; just ensure debug modes are off if any (FastAPI debug, etc., but I think NiceGUI doesn't expose that as separate concept since it's mostly UI code).

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

*   **GPU Support in Docker:** If your fine-tuning uses GPU (via PyTorch or TensorFlow), you'd need to base on a CUDA image or use nvidia's base images and install nicegui there. That goes beyond NiceGUI itself but important for such an app.
    *   For instance, start from `nvidia/cuda:XX.YY-base` and then install Python and libs, or use a prebuilt DL image from PyTorch or TF that has CUDA and then `pip install nicegui`.
    *   Use `--gpus all` when running docker to pass GPUs.

*   **Environment Variables for Config:** NiceGUI respects some env vars:
    *   `PORT`: It will use this as default port if set (common in Heroku, etc. – ensure to override NiceGUI's default). One GitHub issue indicated that `PORT` env could be overridden by nicegui if not careful, but presumably if you call `ui.run(port=os.getenv("PORT", 8080))` you handle it.
    *   `HOST`: similar for host.
    *   `MATPLOTLIB`: as mentioned, set `MATPLOTLIB=false` to skip matplotlib import if not needed.
    *   Possibly `NICEGUI_HEADLESS`: not sure if exists, but maybe to run without launching a browser even if `ui.run(..., native=True)`? But since in Docker there's no display, it will anyway not do GUI.

*   **Reverse Proxy / HTTPS:** In production, often you put Nginx or similar in front. NiceGUI is just a web server – treat it like any FastAPI app. That means:
    *   Use `host=0.0.0.0` to listen to all interfaces (or specific if needed).
    *   Proxy websockets correctly (if using Nginx, ensure upgrade headers etc. for socket.io).
    *   If you need SSL, either terminate at proxy or use a certificate at the app (maybe simpler to do at proxy).
    *   If behind a proxy that handles paths, you might mount NiceGUI at a subpath – not sure if straightforward, likely you'd handle it at routing or in the proxy config.

*   **Scaling:** Since NiceGUI is one process, scaling horizontally means multiple container instances and some form of load balancing. But given it's stateful (each session sticks to one backend unless you share state in a DB), sticky sessions would be needed if behind a load balancer. For our use-case, probably one instance is fine (or at most manually handle distribution of jobs).

*   **Running as service:** If not using Docker, you can still run behind `uvicorn`/`gunicorn`. For example, run `uvicorn main:app --workers 1` (though multiple workers not supported due to single state, so keep 1). Actually NiceGUI's `ui.run()` probably uses uvicorn internally. If you needed to integrate into a larger FastAPI app, you can mount or include NiceGUI's app (the GitHub comment suggests you can use NiceGUI with an existing FastAPI router).

### 8.3 Environment Variables and Config Options

We've mentioned a few environment variables. Let's list the notable ones for NiceGUI configuration:

*   `HOST` / `PORT`: control network binding if not specified in code. Often used in hosting services. If using `ui.run()`, you can just specify these in code from `os.environ`.
*   `MATPLOTLIB`: default "true". If set to "false", NiceGUI will not import matplotlib on startup. This is good if you don't use any plotting features from it, saving memory and time.
*   `NICEGUI_HOME`: Possibly where NiceGUI stores something (not sure if it stores anything like persistence or user uploads).
*   `DEBUG`: Not sure if NiceGUI uses this, but FastAPI uses `app.debug`. There might be a `ui.run(debug=True/False)`.
*   `UVICORN_RELOAD`: If you run in a container with reload, but usually in prod you wouldn't.

Additionally, NiceGUI's `ui.run()` has parameters:
*   `title="Your App"` – sets the page title (the `<title>` tag).
*   `favicon="path_or_emoji"` – you can set a favicon (they even allow emoji or base64).
*   `native=True` – runs in native (desktop window) mode if PyWebview is installed.
*   `reload=False` – to disable the auto-reloader.
*   `port`, `host` – as described.
*   `socketio_trace=True/False` – maybe to enable verbose logging of socket events for debug.
*   Possibly `autoreload_dir` – if you want to watch additional dirs for changes.

**Configuration & Deployment Reference:** The search snippet references "Configuration & Deployment" docs where some of these are detailed. It likely lists env vars and `ui.run` args.

### 8.4 Native Desktop Mode

One standout feature: NiceGUI can open a native window (using an embedded browser via PyWebview). This is akin to an Electron app, meaning you can distribute your app as a desktop application. Key points:

*   To use native mode, you need to `pip install pywebview` (NiceGUI will detect it). If not installed, `ui.run(native=True)` will prompt an error or suggestion to install `pywebview`.
*   When you do `ui.run(native=True)`, instead of opening the system default browser, it opens a desktop window containing the app. This is great for kiosk or end-users who expect a desktop program.
*   On Ubuntu or some Linux, you might need additional packages for Webview (like `webkitgtk`). On Windows/Mac, PyWebview uses built-in WebView components.
*   **Packaging:** You can bundle this into an executable using PyInstaller or similar. The NiceGUI team mentioned packaging as standalone is possible.
*   **Features in native mode:** You can customize the window (size, fullscreen, frameless, etc., likely via parameters to `ui.run` such as `width=...`, `height=...` or through environment). Possibly in docs: "To customize the initial window size and display mode, use the window ..." was hinted (maybe they allow `ui.run(native=True, width=800, height=600, fullscreen=False)` etc).
*   You can still access the app via browser at the same time if you go to `localhost:8080` (unless you specifically restrict it).
*   **Use cases:** If you want to provide this tool to someone non-technical, you could give them an executable that opens with a nice GUI window, so they don't even realize it's a web app.

Given our focus is likely on a web interface in a server environment (for multiple users perhaps), native mode is optional. But it's good to mention for completeness since the user asked for all aspects (and the link referenced an Electron-like capability).

In summary:
*   For server deployment, Docker on a server with host networking or behind proxy is typical.
*   For a desktop app, use native mode and consider packaging.

One more thing: **Persistent storage** – if your app needs to save settings or data, you'll do that in files or a database as usual. NiceGUI provides a simple built-in "storage" that persists across sessions (maybe using SQLite or JSON). The docs mention "easy-to-use per-user and general persistence". That suggests something like:
```python
ui.client.storage.user.put("pref", value)
value = ui.client.storage.user.get("pref")
```
But I'm not certain of API. Possibly they just mean using browser localStorage or cookies via their API. If relevant, check "Storage | NiceGUI" (which appeared in search results) – likely they have 5 built-in storage types (maybe memory, sqlite, redis, etc.). If your project needs user preferences saved, consider exploring that.

## 9. Best Practices and Project Architecture

To ensure your NiceGUI application is maintainable and robust, consider the following best practices in structuring the code and handling common scenarios:

### 9.1 Code Organization and Modularization

Modular code is easier to navigate and update. Rather than one huge `main.py`, split your app into logical components:

*   **Pages as Separate Modules:** If you have multiple pages (using `@ui.page`), you can define each in its own file. For example, `pages/home.py` with a `home_page()` function decorated with `@ui.page('/')`, `pages/monitor.py` for the monitor page, etc. In `main.py`, you would import these modules so that the page routes get registered. This keeps each page's UI definition isolated.

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

*   **Thread Safety:** If you do use threads, be careful when they interact with shared data. Protect with locks if multiple threads write to the same list/dict. Also, as noted, avoid directly manipulating NiceGUI UI elements from background threads. Instead, use a safe pattern (like set a flag and let main thread's timer or next callback update the UI). If you must update from a thread, ensure the NiceGUI docs say it's allowed or not. (Often UI libs are single-threaded; NiceGUI likely is too.)

*   **Large Data in UI:** Sending very large data via the WebSocket (like a huge image or a million rows table) can be slow or crash the browser. For images, consider resizing or compressing. For tables, use pagination or AG Grid's virtualization. For charts, limit data points or decimate if too dense.

*   **Memory Management:** If you display a lot of images or plots, clean them up if not needed. For example, if you keep updating a Matplotlib figure and not using the old ones, ensure references are dropped so Python can GC them. In the browser, if you add elements dynamically without removing old ones, you could inflate memory. Use `.delete()` on NiceGUI elements if available (maybe `element.remove()` or simply design so that you update existing components instead of creating new ones repeatedly).

*   **Session Management:** If multi-user, be mindful of global state. For example, if you have a global list of jobs, prefix entries by user or keep separate structures per user. NiceGUI might allow per-session data via something like `ui.get_client().storage` etc. If one user's action should not affect others, isolate it. Conversely, if it should (like a shared dashboard), handle concurrency (two users starting jobs at same time altering same global list – use locks).

*   **Clean Shutdown:** If your app spawns threads or subprocesses, handle termination. When NiceGUI exits (perhaps user closes window or you hit `Ctrl+C` on server), your threads might still run unless daemonized. Mark threads as daemon or catch the termination signal to instruct them to stop gracefully. This prevents orphan processes.

*   **Security:** NiceGUI doesn't inherently have auth or permission checks. If your app will be deployed on a server accessible by many, consider adding a login page or at least basic HTTP auth in front (perhaps using FastAPI dependencies or an auth proxy). Also validate user inputs (though being a mostly controlled interface, risk is low, but e.g., if a user can input a shell command to run, that's dangerous – apply typical security measures).

*   **Testing:** While we postpone heavy testing discussions, note that NiceGUI includes a pytest plugin for UI tests. You can write tests that spin up the UI and use Playwright to simulate clicks. This is advanced, but if building a serious app, writing some tests for critical UI flows is beneficial. The NiceGUI template's inclusion of test tools hints at this.

### 9.3 Extending NiceGUI (Plugins and Custom Components)

We already saw one extension: `nicegui-highcharts`. There could be others and you can create your own:

*   **Community Extensions:** Check NiceGUI GitHub or community for plugins like `nicegui-template` (for project scaffolding), maybe a `nicegui-<something>` for other JS libs or integrations (for example, maybe someone made `nicegui-d3` or `nicegui-leaflet` for maps, etc.). The installation and usage pattern likely similar to highcharts: install package, import or just call component after installation.

*   **ROSYS Integration:** The template mentioned an option `use_rosys`. RoSys is a robotics framework by Zauberzeug. If that's enabled, it likely pulls in some components or logic for robotics. Not relevant to our case, but worth noting if doing robotics UI, they have synergy.

*   **Custom Vue Component:** If you have a specific front-end widget that NiceGUI doesn't support, you can integrate it. The docs mention the ability to register custom components (maybe using `ui.add_component('tag-name', VueComponent)` or an API to define a Python wrapper for a JS component). For example, if you wanted to use a particular JS chart library that's not available, you could manually include its JS file (via `ui.add_head_html(<script> tag)`) and then use `ui.element('custom-tag')` with appropriate props to instantiate it. For two-way communication, you might need to tap into NiceGUI's socket events. This is advanced and usually not needed because NiceGUI plus Quasar covers a lot.

*   **Contributing to NiceGUI:** If you find a missing feature that would benefit others, consider contributing upstream. The maintainers seem active and welcoming to suggestions (their discussions indicate they continuously improve docs and features).

*   **Performance tuning:** If you eventually want to scale up, consider where bottlenecks might be: heavy computations (move to background or external service), large data through WebSocket (maybe compress or send diff updates), number of concurrent clients (one process can handle many async users if not CPU-bound, but if needed, run multiple instances behind a load balancer with session stickiness).

By adhering to these best practices, your NiceGUI application will be easier to maintain and extend. The goal is to structure it in a way that the UI code is clean and the backend logic (like starting jobs, reading metrics) is separated so it could even be reused or tested independently.

## 10. Summary and Next Steps

In this advanced guide (Part 2), we've covered the sophisticated aspects of developing with NiceGUI:

*   **Data Visualization:** We explored both simple (`ui.table`) and advanced (AG Grid) table components for displaying tabular data, along with charting options including Matplotlib integration and Highcharts for interactive visualizations. We discussed strategies for streaming logs and system metrics to create responsive monitoring interfaces.

*   **Styling and Theming:** You learned how to leverage Quasar props and Tailwind CSS classes to customize the appearance of your application. We covered advanced styling techniques including custom CSS injection, dark mode support, and responsive design patterns.

*   **Deployment:** We reviewed deployment strategies including Docker containerization (both using the official image and building custom images), environment variable configuration, and considerations for production deployment including reverse proxies and scaling. We also touched on the unique native desktop mode capability.

*   **Best Practices:** Finally, we outlined architectural best practices for organizing code into modular components, avoiding common pitfalls like blocking operations and memory issues, and extending NiceGUI through plugins and custom components.

**Combining Both Parts:** Together with Part 1 (Core Concepts), you now have a complete reference for building production-grade web applications with NiceGUI. Part 1 taught you the fundamentals of the framework, component usage, and event handling. Part 2 equipped you with advanced techniques for data presentation, professional styling, and robust deployment.

**Next Steps:** With this comprehensive knowledge:

1. **Initialize Your Project:** Use the NiceGUI template or create a well-structured project following the patterns described in both parts.

2. **Build Your UI:** Start with the core pages and components, implementing the layouts and interactions as described in Part 1.

3. **Add Advanced Features:** Integrate data tables, charts, and real-time monitoring as covered in this part.

4. **Polish and Deploy:** Apply styling, test in both light and dark modes, and prepare for deployment using Docker or native packaging.

5. **Iterate:** As your application grows, refer back to the best practices section to maintain code quality and performance.

Remember, NiceGUI's community is active and helpful. The official documentation (https://nicegui.io) is regularly updated, and the GitHub repository and forum are great resources for specific questions or advanced use cases.

**Final Thoughts:** NiceGUI strikes an excellent balance between ease of use and power. By keeping your Python code as the source of truth while leveraging modern web technologies under the hood, it enables rapid development of sophisticated applications. Whether you're building a machine learning dashboard, IoT control panel, or any data-driven web application, the patterns and practices outlined in this two-part handbook will help you create robust, maintainable, and professional interfaces.

Good luck with your NiceGUI project!

---

## Sources

*   NiceGUI GitHub README (features, usage)
*   NiceGUI SourceForge Summary (overview of capabilities)
*   NiceGUI Highcharts Documentation (usage example)
*   NiceGUI Template Documentation (project setup and options)
*   Medium Article on NiceGUI vs others (data binding, customization)
*   Reddit Q&A and Announcements (native mode, deployment tips)
