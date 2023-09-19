from tkinter import *
from matplotlib import pyplot as plt
import userDatabase
import Main
import yfinance as yf
import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# parameters
username = "username1"
options = Main.get_symbols()

max_symbol = 5
headers = [("Symbol", "Type", "Qty.", "Profit/Loss")]
overall_profit = 0
trade_info = Main.get_trades()
for i in range(len(trade_info)):
    overall_profit += round(trade_info[i][3], 2)
trade_info = headers + trade_info

# check all eligible trade-able symbols
checker = open("data/tradable_symbols", "r")
get_symbols = checker.read()
to_list = get_symbols.split('\n')
checker.close()


# logs in user and connects their account information/establishes API connection to Main.py
def log_in(user):
    global username
    username = user

    print("Logging in...")

    Main.connect(user)
    user_logged_in()


# main logged-in UI
def user_logged_in(window=None):
    if window is not None:
        window.destroy()
    start = Tk()
    start.title("Robo-advisor")
    start.resizable(False, False)

    welcome = Label(start, text=f"Welcome, {username}", font=('Helvetica bold', 25))
    welcome.grid(row=0, column=0, padx=100, pady=30)

    config_button = Button(start, text="Configure variables", height=5, width=20,
                           command=lambda: config_variables(start))
    show_button = Button(start, text="Show activity overview", height=5, width=20,
                         command=lambda: activity_overview(start, trade_info))
    robo_button = Button(start, text="Run robo-advisor", height=5, width=20,
                         command=run_robo_advisor)
    exit_button = Button(start, text="Exit", command=lambda: close(start))

    config_button.grid(row=1, column=0, padx=10, pady=10)
    show_button.grid(row=2, column=0, padx=10, pady=10)
    robo_button.grid(row=3, column=0, padx=10, pady=10)
    exit_button.grid(row=4, column=0, padx=10, pady=30, ipadx=30)

    start.mainloop()


# configure variables UI
def config_variables(window):
    window.destroy()
    variable = Tk()
    variable.title("Configure Variables")
    variable.resizable(False, False)

    budget_range = (50, 5000)
    stop_range = (10, 100)

    is_set = userDatabase.get_trail(username)

    # get company/symbol entry and adds to user's watchlist
    def get_company():
        c_submit = company_entry.get().upper()

        if c_submit in to_list:
            symbol_count = Main.get_symbols()
            if len(symbol_count) < max_symbol:
                add_asset = Main.add_symbols(c_submit)
                if add_asset:
                    error_message.config(text="Symbol submitted", fg="#32a852")
                    company_entry.delete(0, END)
                else:
                    error_message.config(text="Symbol already added", fg="#cf8488")
            else:
                error_message.config(text="Maximum watchlist limit reached", fg="#cf8488")
        else:
            error_message.config(text="Symbol not recognised", fg="#cf8488")

    # get symbols to remove from user's watchlist
    def get_remove():
        r_submit = entry_var.get()
        try:
            options.remove(r_submit)
            Main.remove_symbols(r_submit)
            error_message.config(text="Item removed successfully", fg="#32a852")
        except ValueError:
            error_message.config(text="Item already removed", fg="#cf8488")

    # get budget and stop loss values to add to database
    def get_entries():
        budget_value = budget_entry.get()
        stop_value = stop_loss_entry.get()

        if budget_value != "":
            try:
                budget_value = int(budget_entry.get())

                if budget_value in range(budget_range[0], budget_range[1]):
                    userDatabase.add_budget(budget_value, username)
                    error_message.config(text="Value(s) submitted successfully", fg="#32a852")
                else:
                    error_message.config(text="Budget value must be between $50 and $5000", fg="#cf8488")
                    return False

            except ValueError:
                error_message.config(text="Value(s) must be a number", fg="#cf8488")
                return False

        if stop_value != "":
            try:
                stop_value = int(stop_loss_entry.get())

                if stop_value in range(stop_range[0], stop_range[1]):
                    userDatabase.add_stop_loss(stop_value, username)
                    error_message.config(text="Value(s) submitted successfully", fg="#32a852")
                else:
                    error_message.config(text="Stop loss must be between 10% and 100%", fg="#cf8488")

            except ValueError:
                error_message.config(text="Value(s) must be a number", fg="#cf8488")

    # retrieve checkbox value for user to opt in/out of trailing stop orders
    def submit_trail():
        trail = var_trail.get()
        new_trail = "n"
        if trail == 1:
            new_trail = "y"

        if new_trail != is_set:
            userDatabase.change_trail(new_trail, username)
            error_message.config(text="Settings changed successfully", fg="#32a852")
        else:
            error_message.config(text="Settings already changed", fg="#cf8488")

    company_frame = Frame(variable, highlightbackground="#b8b6b6", highlightthickness=1)
    remove_frame = Frame(variable, highlightbackground="#b8b6b6", highlightthickness=1)
    budget_frame = Frame(variable, highlightbackground="#b8b6b6", highlightthickness=1)
    trail_frame = Frame(variable)

    config_var = Label(variable, text="Configure variables", font=('Helvetica bold', 20))
    company = Label(company_frame, text="Add companies to trade list:")
    remove_company = Label(remove_frame, text="Remove companies from trade list:")
    budget = Label(budget_frame, text="Budget limit ($):")
    stop_loss = Label(budget_frame, text="Stop Loss (%):")
    submit = Button(budget_frame, text="Submit changes", command=get_entries)
    trail_label = Label(variable, text="Trailing Stop Orders do not allow fractional trades, so qty of trade will "
                                       "always be 1.", wraplength=300, font=('TkDefaultFont', 12))
    if is_set == "y":
        var_trail = IntVar(value=1)
    else:
        var_trail = IntVar(value=0)

    trail_or_no = Checkbutton(trail_frame, text="Allow Trailing Orders?", variable=var_trail)
    trail_submit = Button(trail_frame, text="Confirm", height=1, width=6, command=submit_trail)
    error_message = Label(variable, text="")
    go_back = Button(variable, text="Back to Main Menu", command=lambda: user_logged_in(window=variable))

    budget_var = StringVar(variable)
    stop_var = StringVar(variable)
    entry_var = StringVar(variable)

    company_button = Button(company_frame, text="Submit", command=get_company)
    remove_button = Button(remove_frame, text="Submit", command=get_remove)

    company_entry = Entry(company_frame)
    remove_entry = OptionMenu(remove_frame, entry_var, *options)
    budget_entry = Spinbox(budget_frame, from_=budget_range[0], to=budget_range[1], textvariable=budget_var)
    stop_loss_entry = Spinbox(budget_frame, from_=10, to=100, textvariable=stop_var)
    budget_var.set("")
    stop_var.set("")
    entry_var.set("Select company:")

    config_var.grid(row=0, column=0, padx=100, pady=20)

    company_frame.grid(row=1, pady=15)
    company.grid(row=0, padx=70, pady=(15, 0))
    company_entry.grid(row=1, pady=(0, 15))
    company_button.grid(row=1, padx=(0, 5), pady=15, sticky="E")

    remove_frame.grid(row=2, pady=15)
    remove_company.grid(row=0, padx=50, pady=(15, 0))
    remove_entry.grid(row=1, pady=(0, 15))
    remove_button.grid(row=1, padx=(0, 30), pady=15, sticky="E")

    budget_frame.grid(row=3, pady=15)
    budget.grid(row=0, padx=105, pady=(15, 0))
    budget_entry.grid(row=1)

    stop_loss.grid(row=2, pady=(15, 0))
    stop_loss_entry.grid(row=3, pady=(0, 15))
    submit.grid(row=4, pady=20)

    trail_label.grid(row=4, ipadx=5)

    trail_frame.grid(row=5, pady=(15, 0))
    trail_or_no.grid(row=1, column=0, padx=(0, 10), pady=(0, 15))
    trail_submit.grid(row=1, column=1, padx=(10, 0), pady=15, sticky="E")

    error_message.grid(row=6, padx=70, pady=10)

    go_back.grid(row=8, column=0, padx=5, pady=5, sticky="E")

    variable.mainloop()


# activity overview UI
def activity_overview(window, items):
    window.destroy()
    activity = Tk()
    activity.title("Activity Overview")
    activity.resizable(False, False)

    def confirm_close():
        confirm = Tk()
        confirm.title("Are you sure?")
        confirm.resizable(False, False)

        confirm_label = Label(confirm, text="All current open trades will be closed\n Do you wish to proceed?")
        yes_button = Button(confirm, text="Close all trades", command=lambda: close_all(confirm))
        no_button = Button(confirm, text="Go back", command=confirm.destroy)

        confirm_label.grid(row=0, padx=50, pady=20)
        yes_button.grid(row=1, padx=(30, 0), pady=20, sticky="W")
        no_button.grid(row=1, padx=(0, 30), pady=20, sticky="E")

    # closes all trades if users presses button
    def close_all(win):
        win.destroy()
        Main.close_all_trades()

    overview = generate_overview()

    graph_frame = Frame(activity, highlightbackground="#b8b6b6", highlightthickness=1)
    sidebar_frame = Frame(activity, highlightbackground="#b8b6b6", highlightthickness=1.5)

    header = Label(activity, text="Activity Overview", font=('Helvetica bold', 25))
    overall = Label(activity, text=f"Overall Profit:", font=('TkDefaultFont bold', 15))
    overall_num = Label(activity, text=f"${round(overall_profit, 2)}", font=('TkDefaultFont bold', 15))
    if overall_profit > 0:
        overall_num['fg'] = "#32a852"
    else:
        overall_num['fg'] = "#cf8488"
    graph_label = Label(graph_frame, text="Watchlist Performance Overview", font=('TkDefaultFont', 14))
    display_graph = FigureCanvasTkAgg(overview, graph_frame)
    display_graph.draw()
    close_all = Button(activity, text="Close all trades", fg="#cf8488", command=confirm_close)

    for a in range(len(items)):
        for b in range(len(items[0])):
            if a == 0:
                item = Label(sidebar_frame, width=20, text=items[a][b], font=('TkDefaultFont', 15, 'bold'))
            else:
                item = Label(sidebar_frame, width=20, text=items[a][b])
                if type(items[a][b]) == float:
                    if items[a][b] < 0:
                        item['fg'] = "#cf8488"
                    else:
                        item['fg'] = "#32a852"
            item.grid(row=a, column=b)

    header.grid(row=0, column=0, padx=100, pady=20)
    overall.grid(row=1, column=0, padx=30, pady=20, sticky="W")
    overall_num.grid(row=1, column=0, padx=160, pady=20, sticky="W")
    graph_frame.grid(row=2, column=0)
    graph_label.grid(row=0, pady=(20, 0))
    display_graph.get_tk_widget().grid(row=1, pady=(0, 20))
    sidebar_frame.grid(row=3, column=0, padx=20, pady=30)
    # scroll.grid(rowspan=5, column=4)

    close_all.grid(row=4, pady=20)
    go_back = Button(activity, text="Back to Main Menu", command=lambda: user_logged_in(window=activity))
    go_back.grid(row=5, column=0, padx=5, pady=5, sticky="E")

    activity.mainloop()

    # get user data (stocks opted in)
    # retrieve stock info by id (from main)


# run robo-advisor UI
def run_robo_advisor():
    def load():
        open_trades = Main.get_from_ts()
        head_label.config(text="Done!")
        subhead_label.config(text=f"{len(open_trades)} have been opened.")

    ra = Tk()
    ra.title("Loading...")
    ra.resizable(False, False)

    head_label = Label(ra, text="Gathering information...", font=('TkDefaultFont', 15, 'bold'))
    subhead_label = Label(ra, text="This may take a few moments.", font=('TkDefaultFont', 14))
    proceed = Button(ra, text="Proceed", command=load)

    head_label.grid(row=0, padx=200, pady=20)
    subhead_label.grid(row=1, pady=10)
    proceed.grid(row=2, pady=(10, 20))

    ra.mainloop()


# generates graph to be displayed in activity overview
def generate_overview():
    plt.style.use("bmh")
    graph_fig = plt.figure(figsize=(8, 3))
    graph = graph_fig.add_subplot(111)
    today = datetime.datetime.today().date()
    month = today - datetime.timedelta(days=30)
    legend = []

    for a in options:
        data = yf.download(tickers=a, start=month, end=today)
        data = data.reset_index()

        x = data['Date']
        y = data['Close']

        graph.plot(x, y)
        legend.append(a)

    graph.legend(legend)

    return graph_fig


# closes application
def close(application):
    application.destroy()


if __name__ == '__main__':
    log_in(username)
