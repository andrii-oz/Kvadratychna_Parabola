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

        self.is_zoomed = False
        self.last_params: tuple[float, float, float, float, float, float, float] | None = None

        self._build_ui()
        self.plot_graph()

    def _build_ui(self) -> None:
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(0, weight=0)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        left_panel = ttk.Frame(main_frame, width=280, padding=(10, 10, 15, 10))
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
        ttk.Button(btn_frame, text="Розгорнути / Звичайний", command=self.toggle_zoom).pack(fill="x", pady=(6, 0))

        ttk.Separator(left_panel, orient="horizontal").pack(fill="x", pady=8)
        ttk.Label(left_panel, text="Точки перетину з осями").pack(anchor="w")
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

    @staticmethod
    def _add_labeled_entry(parent: ttk.Frame, label_text: str, variable: tk.StringVar) -> None:
        line = ttk.Frame(parent)
        line.pack(fill="x", pady=2)
        ttk.Label(line, text=label_text, width=8).pack(side="left")
        ttk.Entry(line, textvariable=variable).pack(side="left", fill="x", expand=True)

    def toggle_zoom(self) -> None:
        self.is_zoomed = not self.is_zoomed
        self.root.state("zoomed" if self.is_zoomed else "normal")

    @staticmethod
    def _format_num(value: float) -> str:
        if abs(value - round(value)) < 1e-10:
            return str(int(round(value)))
        return f"{value:.4f}"

    def _calculate_intersections(self, a: float, b: float, c: float) -> str:
        lines = [f"З віссю OY: (0; {self._format_num(c)})"]

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

    def _draw_graph(self, a: float, b: float, c: float, xmin: float, xmax: float, ymin: float, ymax: float) -> None:
        self.canvas.delete("all")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 20 or height < 20:
            return

        left_pad = 50
        right_pad = 20
        top_pad = 20
        bottom_pad = 40

        plot_w = max(10, width - left_pad - right_pad)
        plot_h = max(10, height - top_pad - bottom_pad)

        def to_px(x: float, y: float) -> tuple[float, float]:
            px = left_pad + (x - xmin) * plot_w / (xmax - xmin)
            py = top_pad + (ymax - y) * plot_h / (ymax - ymin)
            return px, py

        self.canvas.create_rectangle(
            left_pad,
            top_pad,
            left_pad + plot_w,
            top_pad + plot_h,
            outline="black",
            width=1,
        )

        if xmin <= 0 <= xmax:
            x0, _ = to_px(0, ymin)
            self.canvas.create_line(x0, top_pad, x0, top_pad + plot_h, fill="black", width=1)
        if ymin <= 0 <= ymax:
            _, y0 = to_px(xmin, 0)
            self.canvas.create_line(left_pad, y0, left_pad + plot_w, y0, fill="black", width=1)

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

        self.canvas.create_text(left_pad + plot_w + 10, top_pad + plot_h - 5, text="X", fill="black", anchor="sw")
        self.canvas.create_text(left_pad + 5, top_pad - 5, text="Y", fill="black", anchor="sw")

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

        self.last_params = (a, b, c, xmin, xmax, ymin, ymax)
        self._draw_graph(a, b, c, xmin, xmax, ymin, ymax)
        self.intersections_label.config(text=self._calculate_intersections(a, b, c))


def main() -> None:
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use("clam")
    QuadraticPlotApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
