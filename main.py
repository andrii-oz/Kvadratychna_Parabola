import math
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


class QuadraticPlotApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Графік квадратичної функції")
        self.root.geometry("1200x700")
        self.root.minsize(900, 600)

        self.last_params: tuple[float, float, float, float, float, float, float] | None = None
        self.cursor_in_canvas = False

        self._build_ui()
        self.plot_graph()

    def _build_ui(self) -> None:
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(0, weight=0)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        left_panel = ttk.Frame(main_frame, width=300, padding=(10, 10, 15, 10))
        left_panel.grid(row=0, column=0, sticky="nsw")

        graph_panel = ttk.Frame(main_frame)
        graph_panel.grid(row=0, column=1, sticky="nsew")
        graph_panel.rowconfigure(0, weight=1)
        graph_panel.columnconfigure(0, weight=1)

        ttk.Label(left_panel, text="Квадратична функція y = ax^2 + bx + c").pack(anchor="w", pady=(0, 8))

        self.a_var = tk.StringVar(value="1")
        self.b_var = tk.StringVar(value="0")
        self.c_var = tk.StringVar(value="0")

        self.xmin_var = tk.StringVar(value="-10")
        self.xmax_var = tk.StringVar(value="10")
        self.ymin_var = tk.StringVar(value="-10")
        self.ymax_var = tk.StringVar(value="10")

        self._add_labeled_entry(left_panel, "a:", self.a_var)
        self._add_labeled_entry(left_panel, "b:", self.b_var)
        self._add_labeled_entry(left_panel, "c:", self.c_var)

        ttk.Separator(left_panel, orient="horizontal").pack(fill="x", pady=8)
        ttk.Label(left_panel, text="Діапазон по осі X").pack(anchor="w")
        self._add_labeled_entry(left_panel, "X min:", self.xmin_var)
        self._add_labeled_entry(left_panel, "X max:", self.xmax_var)

        ttk.Label(left_panel, text="Діапазон по осі Y").pack(anchor="w", pady=(8, 0))
        self._add_labeled_entry(left_panel, "Y min:", self.ymin_var)
        self._add_labeled_entry(left_panel, "Y max:", self.ymax_var)

        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(fill="x", pady=(12, 8))
        ttk.Button(btn_frame, text="Побудувати графік", command=self.plot_graph).pack(fill="x")
        ttk.Button(btn_frame, text="Скинути", command=self.reset_coefficients).pack(fill="x", pady=(6, 0))

        ttk.Separator(left_panel, orient="horizontal").pack(fill="x", pady=8)
        ttk.Label(left_panel, text="Вершина та перетини з осями").pack(anchor="w")
        self.intersections_label = ttk.Label(left_panel, text="", justify="left")
        self.intersections_label.pack(anchor="w", pady=(4, 0))

        self.canvas = tk.Canvas(
            graph_panel,
            bg="white",
            highlightthickness=1,
            highlightbackground="black",
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind("<Enter>", self._on_canvas_enter)
        self.canvas.bind("<Leave>", self._on_canvas_leave)
        self.root.bind_all("<MouseWheel>", self._on_mouse_wheel)  # Windows/macOS
        self.root.bind_all("<Button-4>", self._on_mouse_wheel)    # Linux up
        self.root.bind_all("<Button-5>", self._on_mouse_wheel)    # Linux down

    @staticmethod
    def _add_labeled_entry(parent: ttk.Frame, label_text: str, variable: tk.StringVar) -> None:
        line = ttk.Frame(parent)
        line.pack(fill="x", pady=2)
        ttk.Label(line, text=label_text, width=8).pack(side="left")
        ttk.Entry(line, textvariable=variable).pack(side="left", fill="x", expand=True)

    @staticmethod
    def _format_num(value: float) -> str:
        if abs(value - round(value)) < 1e-10:
            return str(int(round(value)))
        return f"{value:.4f}"

    @staticmethod
    def _format_range(value: float) -> str:
        if abs(value) < 1e-12:
            value = 0.0
        text = f"{value:.6f}".rstrip("0").rstrip(".")
        return text if text else "0"

    def _calculate_intersections(self, a: float, b: float, c: float) -> str:
        lines: list[str] = []

        if abs(a) < 1e-12:
            lines.append("Вершина: не визначена (лінійна функція)")
        else:
            vx = -b / (2 * a)
            vy = a * vx * vx + b * vx + c
            lines.append(f"Вершина: ({self._format_num(vx)}; {self._format_num(vy)})")

        lines.append(f"З віссю OY: (0; {self._format_num(c)})")

        if abs(a) < 1e-12:
            if abs(b) < 1e-12:
                if abs(c) < 1e-12:
                    lines.append("З віссю OX: нескінченно багато точок")
                else:
                    lines.append("З віссю OX: немає перетину")
            else:
                x = -c / b
                lines.append(f"З віссю OX: ({self._format_num(x)}; 0)")
            return "\n".join(lines)

        d = b * b - 4 * a * c
        if d < -1e-12:
            lines.append("З віссю OX: немає перетину")
        elif abs(d) <= 1e-12:
            x = -b / (2 * a)
            lines.append(f"З віссю OX: ({self._format_num(x)}; 0)")
        else:
            sqrt_d = math.sqrt(d)
            x1 = (-b - sqrt_d) / (2 * a)
            x2 = (-b + sqrt_d) / (2 * a)
            lines.append(f"З віссю OX: ({self._format_num(x1)}; 0), ({self._format_num(x2)}; 0)")
        return "\n".join(lines)

    def reset_coefficients(self) -> None:
        self.a_var.set("1")
        self.b_var.set("0")
        self.c_var.set("0")
        self.xmin_var.set("-10")
        self.xmax_var.set("10")
        self.ymin_var.set("-10")
        self.ymax_var.set("10")
        self.plot_graph()

    def _on_canvas_enter(self, _event: tk.Event) -> None:
        self.cursor_in_canvas = True

    def _on_canvas_leave(self, _event: tk.Event) -> None:
        self.cursor_in_canvas = False

    def _apply_view(self, a: float, b: float, c: float, xmin: float, xmax: float, ymin: float, ymax: float) -> None:
        self.xmin_var.set(self._format_range(xmin))
        self.xmax_var.set(self._format_range(xmax))
        self.ymin_var.set(self._format_range(ymin))
        self.ymax_var.set(self._format_range(ymax))

        self.last_params = (a, b, c, xmin, xmax, ymin, ymax)
        self._draw_graph(a, b, c, xmin, xmax, ymin, ymax)
        self.intersections_label.config(text=self._calculate_intersections(a, b, c))

    def _on_mouse_wheel(self, event: tk.Event) -> None:
        if self.last_params is None:
            return
        if not self.cursor_in_canvas:
            return

        a, b, c, xmin, xmax, ymin, ymax = self.last_params

        direction = 0
        if hasattr(event, "delta") and event.delta:
            direction = 1 if event.delta > 0 else -1
        elif getattr(event, "num", 0) == 4:
            direction = 1
        elif getattr(event, "num", 0) == 5:
            direction = -1

        if direction == 0:
            return

        zoom_factor = 0.90 if direction > 0 else 1.10

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        left_pad = 55
        right_pad = 20
        top_pad = 20
        bottom_pad = 40
        plot_w = max(10, width - left_pad - right_pad)
        plot_h = max(10, height - top_pad - bottom_pad)

        pointer_x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
        pointer_y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()

        if left_pad <= pointer_x <= left_pad + plot_w and top_pad <= pointer_y <= top_pad + plot_h:
            x_center = xmin + (pointer_x - left_pad) * (xmax - xmin) / plot_w
            y_center = ymax - (pointer_y - top_pad) * (ymax - ymin) / plot_h
        else:
            x_center = (xmin + xmax) / 2
            y_center = (ymin + ymax) / 2

        new_xmin = x_center - (x_center - xmin) * zoom_factor
        new_xmax = x_center + (xmax - x_center) * zoom_factor
        new_ymin = y_center - (y_center - ymin) * zoom_factor
        new_ymax = y_center + (ymax - y_center) * zoom_factor

        min_span = 1e-4
        max_span = 1e8
        if (new_xmax - new_xmin) < min_span or (new_ymax - new_ymin) < min_span:
            return
        if (new_xmax - new_xmin) > max_span or (new_ymax - new_ymin) > max_span:
            return

        self._apply_view(a, b, c, new_xmin, new_xmax, new_ymin, new_ymax)
        self.canvas.update_idletasks()

    def _draw_graph(self, a: float, b: float, c: float, xmin: float, xmax: float, ymin: float, ymax: float) -> None:
        self.canvas.delete("all")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 20 or height < 20:
            return

        left_pad = 55
        right_pad = 20
        top_pad = 20
        bottom_pad = 40

        plot_w = max(10, width - left_pad - right_pad)
        plot_h = max(10, height - top_pad - bottom_pad)

        def to_px(x: float, y: float) -> tuple[float, float]:
            px = left_pad + (x - xmin) * plot_w / (xmax - xmin)
            py = top_pad + (ymax - y) * plot_h / (ymax - ymin)
            return px, py

        # Grid with a 1-unit step.
        grid_color = "#B8B8B8"
        x_start = math.ceil(xmin)
        x_end = math.floor(xmax)
        y_start = math.ceil(ymin)
        y_end = math.floor(ymax)

        for xv in range(x_start, x_end + 1):
            px, _ = to_px(float(xv), ymin)
            self.canvas.create_line(px, top_pad, px, top_pad + plot_h, fill=grid_color, width=1)

        for yv in range(y_start, y_end + 1):
            _, py = to_px(xmin, float(yv))
            self.canvas.create_line(left_pad, py, left_pad + plot_w, py, fill=grid_color, width=1)

        self.canvas.create_rectangle(
            left_pad,
            top_pad,
            left_pad + plot_w,
            top_pad + plot_h,
            outline="black",
            width=1,
        )

        x_axis_y = None
        y_axis_x = None

        if xmin <= 0 <= xmax:
            y_axis_x, _ = to_px(0, ymin)
            self.canvas.create_line(y_axis_x, top_pad, y_axis_x, top_pad + plot_h, fill="black", width=2)
        if ymin <= 0 <= ymax:
            _, x_axis_y = to_px(xmin, 0)
            self.canvas.create_line(left_pad, x_axis_y, left_pad + plot_w, x_axis_y, fill="black", width=2)

        # Direction arrows for axes.
        if x_axis_y is not None:
            self.canvas.create_line(
                left_pad + plot_w - 20,
                x_axis_y,
                left_pad + plot_w - 2,
                x_axis_y,
                fill="black",
                width=2,
                arrow=tk.LAST,
            )
        if y_axis_x is not None:
            self.canvas.create_line(
                y_axis_x,
                top_pad + 20,
                y_axis_x,
                top_pad + 2,
                fill="black",
                width=2,
                arrow=tk.LAST,
            )

        # Tick marks and labels on axes at each integer.
        tick_len_major = 6
        tick_len_half = 4
        tick_len_minor = 2

        if x_axis_y is not None:
            for xv in range(x_start, x_end + 1):
                px, _ = to_px(float(xv), 0.0)
                self.canvas.create_line(px, x_axis_y - tick_len_major, px, x_axis_y + tick_len_major, fill="black", width=1)
                if xv != 0 and xv != x_start and xv != x_end:
                    self.canvas.create_text(px, x_axis_y + 12, text=str(xv), fill="black", anchor="n")

        if y_axis_x is not None:
            for yv in range(y_start, y_end + 1):
                _, py = to_px(0.0, float(yv))
                self.canvas.create_line(y_axis_x - tick_len_major, py, y_axis_x + tick_len_major, py, fill="black", width=1)
                if yv != 0 and yv != y_start and yv != y_end:
                    self.canvas.create_text(y_axis_x - 10, py, text=str(yv), fill="black", anchor="e")

        # Minor ticks at each 0.1 unit; 0.5 unit ticks are medium-sized.
        if x_axis_y is not None:
            minor_x_start = math.ceil(xmin * 10)
            minor_x_end = math.floor(xmax * 10)
            for xi10 in range(minor_x_start, minor_x_end + 1):
                if xi10 % 10 == 0:
                    continue
                x_value = xi10 / 10.0
                px, _ = to_px(x_value, 0.0)
                current_len = tick_len_half if xi10 % 10 == 5 else tick_len_minor
                self.canvas.create_line(px, x_axis_y - current_len, px, x_axis_y + current_len, fill="black", width=1)

        if y_axis_x is not None:
            minor_y_start = math.ceil(ymin * 10)
            minor_y_end = math.floor(ymax * 10)
            for yi10 in range(minor_y_start, minor_y_end + 1):
                if yi10 % 10 == 0:
                    continue
                y_value = yi10 / 10.0
                _, py = to_px(0.0, y_value)
                current_len = tick_len_half if yi10 % 10 == 5 else tick_len_minor
                self.canvas.create_line(y_axis_x - current_len, py, y_axis_x + current_len, py, fill="black", width=1)

        points_count = max(200, min(3000, int(plot_w * 2)))
        step = (xmax - xmin) / (points_count - 1)
        coords: list[float] = []

        for i in range(points_count):
            x = xmin + i * step
            y = a * x * x + b * x + c
            px, py = to_px(x, y)
            coords.extend([px, py])

        if len(coords) >= 4:
            self.canvas.create_line(*coords, fill="black", width=2, smooth=True)

        # Axis names.
        if x_axis_y is not None:
            self.canvas.create_text(left_pad + plot_w - 5, x_axis_y - 12, text="X", fill="black", anchor="se")
        else:
            self.canvas.create_text(left_pad + plot_w - 5, top_pad + plot_h - 5, text="X", fill="black", anchor="se")

        if y_axis_x is not None:
            self.canvas.create_text(y_axis_x + 8, top_pad + 5, text="Y", fill="black", anchor="nw")
        else:
            self.canvas.create_text(left_pad + 6, top_pad + 5, text="Y", fill="black", anchor="nw")

    def _on_canvas_resize(self, _event: tk.Event) -> None:
        if self.last_params is not None:
            self._draw_graph(*self.last_params)

    def plot_graph(self) -> None:
        try:
            a = float(self.a_var.get())
            b = float(self.b_var.get())
            c = float(self.c_var.get())
            xmin = float(self.xmin_var.get())
            xmax = float(self.xmax_var.get())
            ymin = float(self.ymin_var.get())
            ymax = float(self.ymax_var.get())
        except ValueError:
            messagebox.showerror("Помилка", "Введіть коректні числові значення.")
            return

        if xmin >= xmax or ymin >= ymax:
            messagebox.showerror("Помилка", "Мінімум має бути менший за максимум для обох осей.")
            return

        self._apply_view(a, b, c, xmin, xmax, ymin, ymax)


def main() -> None:
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use("clam")
    QuadraticPlotApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
