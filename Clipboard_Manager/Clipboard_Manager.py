import pyperclip
import time
from tkinter import Tk, Listbox, Button, END, Label, Checkbutton, BooleanVar, Menu, font, messagebox, Scrollbar, VERTICAL, RIGHT, Y, BOTH, LEFT, Entry, StringVar

class ClipboardManagerApp:
    def __init__(self):
        self.root = Tk()
        self.root.title("Clipboard Manager")
        self.clipboard_history = []
        self.last_copied_item = None
        self.highlighted_item = None
        self.is_monitoring = True  # Control clipboard monitoring
        self.removed_items = []  # Store removed items for undo

        # Use a modern system font
        self.system_font = font.nametofont("TkDefaultFont")
        self.system_font.configure(family="Segoe UI" if self.is_windows() else "San Francisco", size=12)

        # Initialize UI
        self.setup_ui()

        # Start monitoring clipboard
        self.monitor_clipboard()

        # Run the tkinter main loop
        self.root.mainloop()

    def is_windows(self):
        """Check if the app is running on Windows."""
        import platform
        return platform.system() == "Windows"

    def setup_ui(self):
        """Set up the user interface with a modern color scheme."""
        # Modern color scheme
        self.bg_color = "#F0F0F0"  # Light grey background
        self.fg_color = "#333333"  # Dark grey text
        self.button_bg = "#0078D7"  # Blue button background
        self.button_fg = "black"  # White button text
        self.highlight_color = "#E0E0E0"  # Light grey highlight

        # Apply colors to the root window
        self.root.configure(bg=self.bg_color)

        # Label for clipboard history
        self.label = Label(self.root, text="Clipboard History:", font=self.system_font, bg=self.bg_color, fg=self.fg_color)
        self.label.pack(pady=10)

        # Search bar
        self.search_var = StringVar()
        self.search_var.trace("w", self.filter_history)
        self.search_entry = Entry(self.root, textvariable=self.search_var, font=self.system_font, bg="white", fg=self.fg_color, bd=2, relief="flat")
        self.search_entry.pack(pady=10, fill="x", padx=10)

        # Create a frame to hold the Listbox and Scrollbar
        listbox_frame = Label(self.root, bg=self.bg_color)
        listbox_frame.pack(padx=10, pady=10, fill=BOTH, expand=True)

        # Listbox to display clipboard history
        self.listbox = Listbox(listbox_frame, width=50, height=10, font=self.system_font, bg="white", fg=self.fg_color, bd=2, relief="flat")
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True)

        # Add a vertical scrollbar
        scrollbar = Scrollbar(listbox_frame, orient=VERTICAL)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Link the scrollbar to the Listbox
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)

        # Disable horizontal scroll
        self.listbox.config(width=0)  # Set width to 0 to disable horizontal scroll

        # Bind double-click event to copy selected item
        self.listbox.bind("<Double-Button-1>", self.copy_on_double_click)
        # Bind Enter key to copy selected item
        self.listbox.bind("<Return>", self.copy_on_enter)

        # Label to display the current copied item
        self.copied_item_label = Label(self.root, text="Current Copied Item: None", font=self.system_font, bg=self.bg_color, fg=self.fg_color)
        self.copied_item_label.pack(pady=10)

        # Button to clear clipboard history
        self.clear_button = Button(self.root, text="Clear History", command=self.clear_history, font=self.system_font, bg=self.button_bg, fg=self.button_fg, bd=0, highlightthickness=0)
        self.clear_button.pack(pady=10)

        # Button to remove selected item
        self.remove_button = Button(self.root, text="Remove Selected", command=self.remove_selected, font=self.system_font, bg=self.button_bg, fg=self.button_fg, bd=0, highlightthickness=0)
        self.remove_button.pack(pady=10)

        # Button to undo last removal
        self.undo_button = Button(self.root, text="Undo", command=self.undo_last_removal, font=self.system_font, bg=self.button_bg, fg=self.button_fg, bd=0, highlightthickness=0)
        self.undo_button.pack(pady=10)

        # Checkbutton to toggle "Always on Top"
        self.always_on_top_var = BooleanVar(value=True)
        self.always_on_top_checkbutton = Checkbutton(
            self.root, text="Always on Top", variable=self.always_on_top_var, command=self.toggle_always_on_top, font=self.system_font, bg=self.bg_color, fg=self.fg_color
        )
        self.always_on_top_checkbutton.pack(pady=10)

        # Set the window to be always on top by default
        self.root.attributes("-topmost", True)

        # Tip for users
        self.tip_label = Label(self.root, text="Tip: Double-click an item or press Enter to copy it.", font=self.system_font, bg=self.bg_color, fg=self.fg_color)
        self.tip_label.pack(pady=10)

        # Add a menu bar
        self.create_menu_bar()

    def create_menu_bar(self):
        """Create a menu bar with macOS-like options."""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Quit", command=self.root.quit, accelerator="Cmd+Q" if not self.is_windows() else "Ctrl+Q")
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit menu
        edit_menu = Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Clear History", command=self.clear_history)
        edit_menu.add_command(label="Remove Selected", command=self.remove_selected)
        edit_menu.add_command(label="Undo", command=self.undo_last_removal)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

    def show_about(self):
        """Display an About dialog."""
        messagebox.showinfo("About", "Clipboard Manager\nVersion 1.0\n\nA simple clipboard manager for macOS and Windows.")

    def monitor_clipboard(self):
        """Monitor the clipboard and update the history."""
        if self.is_monitoring:
            current_clipboard = pyperclip.paste()
            if current_clipboard not in self.clipboard_history:
                self.clipboard_history.append(current_clipboard)
                self.listbox.insert(END, self.truncate_text(current_clipboard))
        self.root.after(1000, self.monitor_clipboard)  # Check clipboard every second

    def truncate_text(self, text, max_length=50):
        """Truncate text to a maximum length."""
        return text[:max_length] + "..." if len(text) > max_length else text

    def filter_history(self, *args):
        """Filter the clipboard history based on the search term."""
        search_term = self.search_var.get().lower()
        self.listbox.delete(0, END)
        for item in self.clipboard_history:
            if search_term in item.lower():
                self.listbox.insert(END, self.truncate_text(item))

    def copy_on_double_click(self, event):
        """Copy the selected item to the clipboard when double-clicked."""
        self.copy_item()

    def copy_on_enter(self, event):
        """Copy the selected item to the clipboard when Enter key is pressed."""
        self.copy_item()

    def copy_item(self):
        """Copy the selected item to the clipboard and update the GUI."""
        selected_index = self.listbox.curselection()
        if selected_index:  # Check if an item is selected
            selected_item = self.clipboard_history[selected_index[0]]  # Get the full item from history
            if selected_item != self.last_copied_item:  # Only copy if it's a new selection
                pyperclip.copy(selected_item)
                self.last_copied_item = selected_item  # Update the last copied item

                # Update the label to show the current copied item with a timestamp
                timestamp = time.strftime("%I:%M:%S %p")  # Format: HH:MM:SS AM/PM
                self.copied_item_label.config(text=f"Current Copied Item: {self.truncate_text(selected_item)} (Copied at {timestamp})")

                # Highlight the copied item in the listbox
                self.highlight_copied_item(selected_index)

    def highlight_copied_item(self, index):
        """Highlight the copied item in the listbox."""
        if self.highlighted_item is not None:
            self.listbox.itemconfig(self.highlighted_item, bg="white")  # Reset previous highlight
        self.listbox.itemconfig(index, bg=self.highlight_color)  # Highlight the new item
        self.highlighted_item = index  # Track the highlighted item

    def clear_history(self):
        """Clear the entire clipboard history."""
        self.clipboard_history.clear()
        self.listbox.delete(0, END)
        self.last_copied_item = None  # Reset the last copied item
        self.copied_item_label.config(text="Current Copied Item: None")  # Reset the label
        if self.highlighted_item is not None:
            self.listbox.itemconfig(self.highlighted_item, bg="white")  # Reset highlight
            self.highlighted_item = None

    def remove_selected(self):
        """Remove the selected item from the clipboard history."""
        selected_index = self.listbox.curselection()
        if selected_index:  # Check if an item is selected
            selected_item = self.clipboard_history[selected_index[0]]
            self.is_monitoring = False  # Disable clipboard monitoring
            self.clipboard_history.pop(selected_index[0])  # Remove from the history list
            self.listbox.delete(selected_index)  # Remove from the Listbox
            self.removed_items.append((selected_index[0], selected_item))  # Store for undo
            self.is_monitoring = True  # Re-enable clipboard monitoring

            # Update the last copied item if it was removed
            if selected_item == self.last_copied_item:
                self.last_copied_item = None
                self.copied_item_label.config(text="Current Copied Item: None")

            # Reset highlight if the highlighted item was removed
            if selected_index == self.highlighted_item:
                self.highlighted_item = None

    def undo_last_removal(self):
        """Undo the last removal."""
        if self.removed_items:
            index, item = self.removed_items.pop()
            self.clipboard_history.insert(index, item)
            self.listbox.insert(index, self.truncate_text(item))

    def toggle_always_on_top(self):
        self.root.attributes("-topmost", self.always_on_top_var.get())


if __name__ == "__main__":
    # Run the clipboard manager
    app = ClipboardManagerApp()
