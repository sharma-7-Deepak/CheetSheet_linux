import os
import google.generativeai as genai
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, font
from threading import Thread

# Set up Gemini API
API_KEY = "AIzaSyAk0CDdyUjhdqjpQ_NegHujeZiY5Ila-50"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel()

class CompactCommandExplainer:
    def __init__(self, root):
        self.root = root
        self.root.title("Shell Command Explainer")
        self.root.geometry("600x500")  # Smaller window size
        self.root.resizable(True, True)
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
        # Custom font for better readability
        custom_font = font.Font(family="Helvetica", size=9)  # Smaller font size
        
        # Header
        header_frame = tk.Frame(self.root, bg="#4285F4", height=60)  # Smaller header
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame, 
            text="Shell Command Explainer", 
            font=("Helvetica", 14, "bold"),  # Smaller title font
            fg="white", 
            bg="#4285F4"
        )
        title_label.pack(pady=10)  # Less padding
        
        subtitle_label = tk.Label(
            header_frame, 
            text="Powered by Gemini AI", 
            font=("Helvetica", 8),  # Smaller subtitle font
            fg="white", 
            bg="#4285F4"
        )
        subtitle_label.pack()
        
        # Main content
        main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=15, pady=15)  # Less padding
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input section
        input_frame = tk.Frame(main_frame, bg="#f0f0f0")
        input_frame.pack(fill=tk.X, pady=(0, 8))  # Less padding
        
        tk.Label(
            input_frame, 
            text="Enter shell command:", 
            font=custom_font, 
            bg="#f0f0f0"
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        self.command_entry = ttk.Entry(
            input_frame, 
            width=40,  # Narrower entry
            font=custom_font
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.command_entry.bind("<Return>", lambda e: self.explain_command())
        
        explain_button = ttk.Button(
            input_frame, 
            text="Explain", 
            command=self.explain_command,
            style="Accent.TButton"
        )
        explain_button.pack(side=tk.LEFT, padx=(8, 0))
        
        # Output section
        output_frame = tk.Frame(main_frame, bg="#ffffff", bd=1, relief=tk.GROOVE)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame, 
            wrap=tk.WORD,
            font=custom_font, 
            padx=8, 
            pady=8,
            bg="white",
            fg="#333333",
            width=60,  # Adjusted width
            height=15,  # Adjusted height
            spacing1=3,  # Less spacing
            spacing2=1,
            tabs=('0.4in', 'right')
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        status_bar = tk.Label(
            self.root, 
            textvariable=self.status_var, 
            bd=1, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            bg="#e0e0e0",
            fg="#333333",
            font=custom_font
        )
        status_bar.pack(fill=tk.X)
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure("TButton", padding=4)  # Smaller button padding
        self.style.configure("Accent.TButton", background="#4285F4", foreground="#4285F4")
        self.style.map("Accent.TButton",
                      background=[("active", "#3367D6"), ("disabled", "#cccccc")])
    
    def explain_command(self):
        command = self.command_entry.get().strip()
        if not command:
            messagebox.showwarning("Input Error", "Please enter a command to explain")
            return
        
        if command.lower() in ('exit', 'quit'):
            self.root.destroy()
            return
        
        self.status_var.set("Fetching explanation...")
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"Command: {command}\n\n")
        self.output_text.config(state=tk.DISABLED)
        
        # Disable controls during processing
        self.command_entry.config(state=tk.DISABLED)
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.config(state=tk.DISABLED)
        
        Thread(target=self.fetch_explanation, args=(command,), daemon=True).start()
    
    def fetch_explanation(self, command):
        try:
            prompt = f"""Explain the shell command: {command}
            Be concise but include:
            1. Command purpose
            2. Common usage
            3. Key options
            4. Examples"""
            
            response = model.generate_content(prompt)
            explanation = response.text.strip()
            
            self.root.after(0, self.display_result, explanation)
        except Exception as e:
            self.root.after(0, self.display_error, str(e))
    
    def display_result(self, explanation):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, explanation)
        self.output_text.see(tk.END)  # Auto-scroll to show beginning
        self.output_text.config(state=tk.DISABLED)
        self.status_var.set("Ready")
        self.enable_controls()
    
    def display_error(self, error_msg):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, f"\nError: {error_msg}")
        self.output_text.config(state=tk.DISABLED)
        self.status_var.set("Error occurred")
        self.enable_controls()
    
    def enable_controls(self):
        self.command_entry.config(state=tk.NORMAL)
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = CompactCommandExplainer(root)
    root.mainloop()