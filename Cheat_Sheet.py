import google.generativeai as genai
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, font
from threading import Thread

# Set up Gemini API
API_KEY = "AIzaSyAk0CDdyUjhdqjpQ_NegHujeZiY5Ila-50"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

class CommandExplainer:
    def __init__(self, root):
        self.root = root
        self.root.title("Shell Command Explainer")
        self.root.geometry("650x550")
        self.root.configure(bg="#f0f0f0")
        
        self.setup_ui()
        self.center_window()
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        # Fonts
        custom_font = font.Font(family="Consolas", size=10)
        bold_font = font.Font(family="Consolas", size=10, weight="bold")
        
        # Header
        header_frame = tk.Frame(self.root, bg="#4285F4", height=60)
        header_frame.pack(fill=tk.X)
        
        tk.Label(
            header_frame, 
            text="Shell Command Explainer", 
            font=("Helvetica", 14, "bold"),
            fg="white", 
            bg="#4285F4"
        ).pack(pady=10)
        
        # Main content
        main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input section
        input_frame = tk.Frame(main_frame, bg="#f0f0f0")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            input_frame, 
            text="Enter command:", 
            font=custom_font, 
            bg="#f0f0f0"
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        self.command_entry = ttk.Entry(input_frame, width=45, font=custom_font)
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.command_entry.bind("<Return>", lambda e: self.explain_command())
        
        ttk.Button(
            input_frame, 
            text="Explain", 
            command=self.explain_command
        ).pack(side=tk.LEFT, padx=(8, 0))
        
        # Output section
        output_frame = tk.Frame(main_frame, bg="#ffffff", bd=1, relief=tk.GROOVE)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame, 
            wrap=tk.WORD,
            font=custom_font,
            bg="white",
            fg="#333333",
            padx=10,
            pady=10,
            spacing1=5,
            spacing2=2,
            tabs=('0.5in', 'right')
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags
        self.output_text.tag_config('command', font=bold_font, foreground='#0066CC')
        self.output_text.tag_config('heading', font=bold_font, foreground='#4285F4', spacing3=8)
        self.output_text.tag_config('option', font=custom_font, foreground='#0F9D58')
        self.output_text.tag_config('example', font=custom_font, foreground='#EA4335')
        self.output_text.tag_config('normal', font=custom_font)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        tk.Label(
            self.root, 
            textvariable=self.status_var, 
            bd=1, relief=tk.SUNKEN, anchor=tk.W,
            bg="#e0e0e0", fg="#333333", font=custom_font
        ).pack(fill=tk.X)
    
    def explain_command(self):
        command = self.command_entry.get().strip()
        if not command:
            messagebox.showwarning("Input Error", "Please enter a command")
            return
        
        self.status_var.set("Generating explanation...")
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"Command: ", 'normal')
        self.output_text.insert(tk.END, f"{command}\n\n", 'command')
        self.output_text.config(state=tk.DISABLED)
        
        self.command_entry.config(state=tk.DISABLED)
        Thread(target=self.fetch_explanation, args=(command,), daemon=True).start()
    
    def fetch_explanation(self, command):
        try:
            prompt = f"""Explain the shell command: {command}
            Format the response EXACTLY like this without any asterisks or markdown:

            PURPOSE
            [Brief description of what the command does]

            USAGE
            [Basic command syntax]
            [Parameters explanation if needed]

            OPTIONS
            -option  [Description]
            -option  [Description]

            EXAMPLES
            1. example_command [Description]
            2. example_command [Description]
            
            Keep it concise and use proper spacing."""
            
            response = model.generate_content(prompt)
            self.root.after(0, self.display_result, response.text)
        except Exception as e:
            self.root.after(0, self.display_error, str(e))
    
    def display_result(self, explanation):
        self.output_text.config(state=tk.NORMAL)
        
        # Process and format the explanation
        lines = explanation.split('\n')
        for line in lines:
            if line.startswith('PURPOSE') or line.startswith('USAGE') or line.startswith('OPTIONS') or line.startswith('EXAMPLES'):
                self.output_text.insert(tk.END, f"\n{line}\n", 'heading')
            elif line.strip().startswith('-'):
                parts = line.split(' ', 1)
                if len(parts) > 1:
                    self.output_text.insert(tk.END, f"  {parts[0]} ", 'option')
                    self.output_text.insert(tk.END, f"{parts[1]}\n", 'normal')
            elif line.strip() and line[0].isdigit() and '.' in line:
                parts = line.split(' ', 1)
                if len(parts) > 1:
                    self.output_text.insert(tk.END, f"{parts[0]} ", 'example')
                    self.output_text.insert(tk.END, f"{parts[1]}\n", 'normal')
            else:
                self.output_text.insert(tk.END, f"{line}\n", 'normal')
        
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.status_var.set("Ready")
        self.command_entry.config(state=tk.NORMAL)
    
    def display_error(self, error_msg):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, f"\nError: {error_msg}\n", 'normal')
        self.output_text.config(state=tk.DISABLED)
        self.status_var.set("Error occurred")
        self.command_entry.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = CommandExplainer(root)
    root.mainloop()
