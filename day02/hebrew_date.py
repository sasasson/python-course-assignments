def gregorian_to_hebrew(year: int, month: int, day: int) -> dict:
    """
    Convert a Gregorian date to a Hebrew date.

    Returns a dict with keys:
      - year (int)       : Hebrew year
      - month (int)      : Hebrew month number (1..13)
      - day (int)        : Hebrew day (1..30)
      - month_name (str) : Human-readable month name (Adar II handled)
      - formatted (str)  : e.g. "5 Nisan 5785"

    Requires the 'convertdate' package. Install with:
      python -m pip install convertdate

    Example:
      >>> gregorian_to_hebrew(2025, 11, 7)
      {'year': 5786, 'month': 8, 'day': 1, 'month_name': 'Cheshvan', 'formatted': '1 Cheshvan 5786'}
    """
    try:
        # import hebrew implementation
        import convertdate.hebrew as hebrew
    except Exception:
        raise ImportError("This function requires the 'convertdate' package (missing 'hebrew' module). "
                          "Install with: python -m pip install convertdate")

    # convertdate exposes julian-day helpers under different names across versions
    # try a few common module names (julianday, daycount, utils.julianday)
    jd = None
    jd_candidates = [
        "convertdate.julianday",
        "convertdate.daycount",
        "convertdate.jd",
        "convertdate.utils",
    ]
    for cand in jd_candidates:
        try:
            module = __import__(cand, fromlist=["*"])
            # prefer modules that expose from_gregorian / to_gregorian
            if hasattr(module, "from_gregorian") and hasattr(module, "to_gregorian"):
                jd = module
                break
            # if module is a utils package, check for a submodule named 'julianday'
            if cand.endswith("utils"):
                try:
                    sub = __import__(cand + ".julianday", fromlist=["*"])
                    if hasattr(sub, "from_gregorian") and hasattr(sub, "to_gregorian"):
                        jd = sub
                        break
                except Exception:
                    pass
        except Exception:
            continue

    if jd is None:
        raise ImportError("This function requires the 'convertdate' package with a julianday helper (tried: julianday, daycount, jd). "
                          "Install or upgrade convertdate: python -m pip install --upgrade convertdate")

    # convert Gregorian to Julian day then to Hebrew
    j = jd.from_gregorian(year, month, day)
    h_year, h_month, h_day = hebrew.from_jd(j)

    # month names (index for 1..13; 13 -> Adar II)
    HEBREW_MONTH_NAMES = [
        "Nisan", "Iyar", "Sivan", "Tamuz", "Av", "Elul",
        "Tishri", "Cheshvan", "Kislev", "Tevet", "Shevat",
        "Adar", "Adar II"
    ]

    if h_month == 13:
        month_name = "Adar II"
    else:
        month_name = HEBREW_MONTH_NAMES[h_month - 1]

    formatted = f"{int(h_day)} {month_name} {int(h_year)}"

    return {
        "year": int(h_year),
        "month": int(h_month),
        "day": int(h_day),
        "month_name": month_name,
        "formatted": formatted,
    }


def _cli():
    import argparse
    parser = argparse.ArgumentParser(description="Convert Gregorian date to Hebrew date")
    parser.add_argument("year", type=int, nargs="?", help="Gregorian year")
    parser.add_argument("month", type=int, nargs="?", help="Gregorian month (1-12)")
    parser.add_argument("day", type=int, nargs="?", help="Gregorian day (1-31)")
    parser.add_argument("--mode", choices=["cli", "interactive", "gui"], default="cli",
                        help="Interface mode: cli (default), interactive (prompts), gui (Tkinter)")
    args = parser.parse_args()

    mode = args.mode
    if mode == "interactive":
        interactive_input()
        return
    if mode == "gui":
        try:
            run_gui()
        except Exception:
            print("GUI failed to start. Try interactive mode instead.")
        return

    # CLI mode: if year/month/day are missing, fall back to interactive prompt
    if args.year is None or args.month is None or args.day is None:
        print("No date provided — switching to interactive input mode.")
        interactive_input()
        return

    try:
        res = gregorian_to_hebrew(args.year, args.month, args.day)
    except ImportError as e:
        print(str(e))
        print("Install with: python -m pip install convertdate")
        return

    print(res["formatted"])


def interactive_input() -> None:
    """Prompt the user for a Gregorian date using input() and print the Hebrew date.

    This function is useful when running the script in a REPL or when the
    user wants to type the date interactively.
    """
    try:
        y_str = input("Enter Gregorian year (e.g. 2025): ").strip()
        if not y_str:
            print("No input received. Exiting.")
            return
        y = int(y_str)
        m = int(input("Enter Gregorian month (1-12): ").strip())
        d = int(input("Enter Gregorian day (1-31): ").strip())
    except ValueError:
        print("Invalid input — please enter integer values for year, month and day")
        return

    try:
        res = gregorian_to_hebrew(y, m, d)
    except ImportError as e:
        print(str(e))
        print("Install with: python -m pip install convertdate")
        return

    print(res["formatted"])


def run_gui() -> None:
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
    except Exception:
        raise

    def on_convert():
        try:
            y = int(year_var.get())
            m = int(month_var.get())
            d = int(day_var.get())
        except ValueError:
            messagebox.showerror("Input error", "Please enter valid integers for year, month and day")
            return

        try:
            res = gregorian_to_hebrew(y, m, d)
        except ImportError:
            messagebox.showerror("Missing dependency", "Please install 'convertdate' (pip install convertdate)")
            return
        except Exception as exc:
            messagebox.showerror("Conversion error", str(exc))
            return

        result_var.set(res["formatted"])

    root = tk.Tk()
    root.title("Gregorian → Hebrew date")

    frm = ttk.Frame(root, padding=12)
    frm.grid()

    ttk.Label(frm, text="Year:").grid(column=0, row=0, sticky="e")
    year_var = tk.StringVar(value=str(2025))
    ttk.Entry(frm, textvariable=year_var, width=10).grid(column=1, row=0)

    ttk.Label(frm, text="Month:").grid(column=0, row=1, sticky="e")
    month_var = tk.StringVar(value=str(11))
    ttk.Entry(frm, textvariable=month_var, width=10).grid(column=1, row=1)

    ttk.Label(frm, text="Day:").grid(column=0, row=2, sticky="e")
    day_var = tk.StringVar(value=str(7))
    ttk.Entry(frm, textvariable=day_var, width=10).grid(column=1, row=2)

    ttk.Button(frm, text="Convert", command=on_convert).grid(column=0, row=3, columnspan=2, pady=8)

    result_var = tk.StringVar(value="")
    ttk.Label(frm, textvariable=result_var, foreground="blue").grid(column=0, row=4, columnspan=2)

    root.mainloop()


if __name__ == "__main__":
    _cli()
