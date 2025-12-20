import tkinter as tk

from ui import PromptMLOUI


def main() -> None:
    root = tk.Tk()
    root.title("PromptMLO Studio")
    app = PromptMLOUI(root)
    app.pack(fill=tk.BOTH, expand=True)
    root.minsize(600, 400)
    root.mainloop()


if __name__ == "__main__":
    main()
