#!/usr/bin/env python3
import json
import os
import sys
import shutil
import re
import glob
import platform
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from datetime import datetime

class Schedule1ModTool:
    def __init__(self, save_path=None):
        """Initialize the mod tool with the path to the save folder."""
        self.save_path = save_path
        self.products_data = None
        self.backup_made = False
        
    def set_save_path(self, path):
        """Set the path to the save folder."""
        self.save_path = path
        
    def make_backup(self):
        """Create a backup of the save folder."""
        if self.backup_made:
            return True
            
        if not self.save_path or not os.path.exists(self.save_path):
            return False
            
        backup_path = f"{self.save_path}_backup_{self._get_timestamp()}"
        try:
            shutil.copytree(self.save_path, backup_path)
            self.backup_made = True
            return True
        except Exception as e:
            return False
    
    def _get_timestamp(self):
        """Get a timestamp string for backup naming."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def load_products_data(self):
        """Load the Products.json file."""
        if not self.save_path:
            return False
            
        products_path = os.path.join(self.save_path, "Products.json")
        if not os.path.exists(products_path):
            return False
            
        try:
            with open(products_path, 'r') as f:
                self.products_data = json.load(f)
            return True
        except Exception:
            return False
    
    def get_product_list(self):
        """Get a list of all products."""
        if not self.products_data:
            if not self.load_products_data():
                return []
        
        return self.products_data["DiscoveredProducts"]
    
    def get_product_details(self):
        """Get detailed product information with names."""
        products = self.get_product_list()
        if not products:
            return []
            
        details = []
        created_products_dir = os.path.join(self.save_path, "CreatedProducts")
        
        for product_id in products:
            product_file = os.path.join(created_products_dir, f"{product_id}.json")
            name = product_id
            product_type = "Unknown"
            properties = []
            
            if os.path.exists(product_file):
                try:
                    with open(product_file, 'r') as f:
                        product_data = json.load(f)
                    name = product_data["Name"]
                    product_type = product_data.get("DataType", "Unknown")
                    properties = product_data.get("Properties", [])
                except:
                    pass
                    
            details.append({
                "id": product_id,
                "name": name,
                "type": product_type,
                "properties": properties
            })
            
        return sorted(details, key=lambda x: x["id"])
    
    def rename_product(self, old_id, new_name):
        """Rename a product's display name but keep the same ID."""
        if not self.products_data:
            if not self.load_products_data():
                return False
        
        # Make sure we have a backup
        if not self.backup_made:
            if not self.make_backup():
                return False
        
        # Find the product file in CreatedProducts folder
        product_file = os.path.join(self.save_path, "CreatedProducts", f"{old_id}.json")
        if not os.path.exists(product_file):
            return False
        
        # Update the product name in its individual file
        try:
            with open(product_file, 'r') as f:
                product_data = json.load(f)
            
            # Update the name
            product_data["Name"] = new_name
            
            with open(product_file, 'w') as f:
                json.dump(product_data, f, indent=4)
            
            return True
        except Exception:
            return False
    
    def change_product_id(self, old_id, new_id, new_name=None):
        """Change a product's ID and optionally its name."""
        if not self.products_data:
            if not self.load_products_data():
                return False
        
        # Make sure we have a backup
        if not self.backup_made:
            if not self.make_backup():
                return False
        
        # Check if the old ID exists and new ID doesn't already exist
        if old_id not in self.products_data["DiscoveredProducts"]:
            return False
        
        if new_id in self.products_data["DiscoveredProducts"]:
            return False
        
        # Find the product file in CreatedProducts folder
        old_product_file = os.path.join(self.save_path, "CreatedProducts", f"{old_id}.json")
        if not os.path.exists(old_product_file):
            return False
        
        # Update the product ID in its individual file
        try:
            with open(old_product_file, 'r') as f:
                product_data = json.load(f)
            
            # Update the ID and optionally the name
            product_data["ID"] = new_id
            if new_name:
                product_data["Name"] = new_name
            
            # Save to new file
            new_product_file = os.path.join(self.save_path, "CreatedProducts", f"{new_id}.json")
            with open(new_product_file, 'w') as f:
                json.dump(product_data, f, indent=4)
            
            # Remove the old file
            os.remove(old_product_file)
            
            # Update all references in Products.json
            self._update_references_in_products_json(old_id, new_id)
            
            return True
        except Exception:
            return False
    
    def _update_references_in_products_json(self, old_id, new_id):
        """Update all references to a product ID in Products.json."""
        # Update discovered products list
        for i, product in enumerate(self.products_data["DiscoveredProducts"]):
            if product == old_id:
                self.products_data["DiscoveredProducts"][i] = new_id
        
        # Update mix recipes
        for recipe in self.products_data["MixRecipes"]:
            if recipe["Product"] == old_id:
                recipe["Product"] = new_id
            if recipe["Mixer"] == old_id:
                recipe["Mixer"] = new_id
            if recipe["Output"] == old_id:
                recipe["Output"] = new_id
        
        # Update product prices
        for price_entry in self.products_data["ProductPrices"]:
            if price_entry["String"] == old_id:
                price_entry["String"] = new_id
        
        # Update favorited products
        for i, product in enumerate(self.products_data["FavouritedProducts"]):
            if product == old_id:
                self.products_data["FavouritedProducts"][i] = new_id
        
        # Save the updated Products.json
        products_path = os.path.join(self.save_path, "Products.json")
        with open(products_path, 'w') as f:
            json.dump(self.products_data, f, indent=4)
    
    def bulk_rename_from_list(self, rename_list):
        """Rename multiple products from a list of tuples."""
        if not self.products_data:
            if not self.load_products_data():
                return False
                
        if not self.backup_made:
            if not self.make_backup():
                return False
                
        success_count = 0
        error_count = 0
        
        for rename_item in rename_list:
            if len(rename_item) < 2:
                continue
                
            old_id = rename_item[0]
            
            # If there are 3 parts, we're changing the ID and name
            if len(rename_item) >= 3:
                new_id = rename_item[1]
                new_name = rename_item[2]
                if self.change_product_id(old_id, new_id, new_name):
                    success_count += 1
                else:
                    error_count += 1
            # If there are 2 parts, we're just changing the name
            else:
                new_name = rename_item[1]
                if self.rename_product(old_id, new_name):
                    success_count += 1
                else:
                    error_count += 1
        
        return success_count, error_count

def find_save_folders():
    """Find all Schedule 1 save folders on the system."""
    saves = []
    system = platform.system()
    
    if system == "Windows":
        # Windows path - look directly in the user profile
        import ctypes.wintypes
        CSIDL_PROFILE = 40
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PROFILE, None, 0, buf)
        user_profile = buf.value
        
        base_path = os.path.join(user_profile, "AppData", "LocalLow", "TVGS", "Schedule I", "Saves")
        
        if os.path.exists(base_path):
            # Look for Steam ID folders
            steam_id_folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
            for steam_id in steam_id_folders:
                steam_folder = os.path.join(base_path, steam_id)
                
                # Check for "save" folder (original path structure)
                save_folder = os.path.join(steam_folder, "save")
                if os.path.exists(save_folder) and os.path.exists(os.path.join(save_folder, "Products.json")):
                    saves.append((f"Steam ID: {steam_id} (save)", save_folder))
                
                # Check for "SaveGame_X" folders (new path structure)
                save_game_folders = [f for f in os.listdir(steam_folder) 
                                   if os.path.isdir(os.path.join(steam_folder, f)) and f.startswith("SaveGame_")]
                for save_game in save_game_folders:
                    save_game_folder = os.path.join(steam_folder, save_game)
                    # Check if Products.json or Products folder exists
                    if os.path.exists(os.path.join(save_game_folder, "Products.json")):
                        saves.append((f"Steam ID: {steam_id} ({save_game})", save_game_folder))
                    elif os.path.exists(os.path.join(save_game_folder, "Products")):
                        products_folder = os.path.join(save_game_folder, "Products")
                        if os.path.exists(os.path.join(products_folder, "Products.json")):
                            saves.append((f"Steam ID: {steam_id} ({save_game}/Products)", products_folder))

    elif system == "Darwin":
        # Similar changes for macOS
        base_path = os.path.expanduser("~/Library/Application Support/TVGS/Schedule I/Saves")
        if os.path.exists(base_path):
            # Same pattern as Windows code
            steam_id_folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
            for steam_id in steam_id_folders:
                steam_folder = os.path.join(base_path, steam_id)
                
                # Check for "save" folder
                save_folder = os.path.join(steam_folder, "save")
                if os.path.exists(save_folder) and os.path.exists(os.path.join(save_folder, "Products.json")):
                    saves.append((f"Steam ID: {steam_id} (save)", save_folder))
                
                # Check for "SaveGame_X" folders
                save_game_folders = [f for f in os.listdir(steam_folder) 
                                   if os.path.isdir(os.path.join(steam_folder, f)) and f.startswith("SaveGame_")]
                for save_game in save_game_folders:
                    save_game_folder = os.path.join(steam_folder, save_game)
                    if os.path.exists(os.path.join(save_game_folder, "Products.json")):
                        saves.append((f"Steam ID: {steam_id} ({save_game})", save_game_folder))
                    elif os.path.exists(os.path.join(save_game_folder, "Products")):
                        products_folder = os.path.join(save_game_folder, "Products")
                        if os.path.exists(os.path.join(products_folder, "Products.json")):
                            saves.append((f"Steam ID: {steam_id} ({save_game}/Products)", products_folder))
    else:
        # Linux path with similar changes
        base_path = os.path.expanduser("~/.config/unity3d/TVGS/Schedule I/Saves")
        if os.path.exists(base_path):
            # Same pattern as Windows code
            steam_id_folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
            for steam_id in steam_id_folders:
                steam_folder = os.path.join(base_path, steam_id)
                
                # Check for "save" folder
                save_folder = os.path.join(steam_folder, "save")
                if os.path.exists(save_folder) and os.path.exists(os.path.join(save_folder, "Products.json")):
                    saves.append((f"Steam ID: {steam_id} (save)", save_folder))
                
                # Check for "SaveGame_X" folders
                save_game_folders = [f for f in os.listdir(steam_folder) 
                                   if os.path.isdir(os.path.join(steam_folder, f)) and f.startswith("SaveGame_")]
                for save_game in save_game_folders:
                    save_game_folder = os.path.join(steam_folder, save_game)
                    if os.path.exists(os.path.join(save_game_folder, "Products.json")):
                        saves.append((f"Steam ID: {steam_id} ({save_game})", save_game_folder))
                    elif os.path.exists(os.path.join(save_game_folder, "Products")):
                        products_folder = os.path.join(save_game_folder, "Products")
                        if os.path.exists(os.path.join(products_folder, "Products.json")):
                            saves.append((f"Steam ID: {steam_id} ({save_game}/Products)", products_folder))
    
    return saves

class ScheduleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Schedule 1 Strain Renamer")
        self.root.geometry("950x700")
        self.root.minsize(800, 600)
        
        # Create the mod tool instance
        self.mod_tool = Schedule1ModTool()
        
        # Set theme based on platform
        self.style = ttk.Style()
        if platform.system() == "Windows":
            # Use native Windows theme for better appearance
            self.style.theme_use('vista')
            
            # Configure colors for Windows - use a nicer color scheme
            self.bg_color = "#F0F0F0"  # Standard Windows background
            self.fg_color = "#000000"  # Black text
            self.highlight_color = "#E0E0E0"  # Light gray highlight
            self.accent_color = "#4527A0"  # Deeper purple accent that looks good on Windows
            
            # Set tab size on Windows (they're too small by default)
            self.style.configure('TNotebook.Tab', padding=[12, 4])
            
            # Configure a nicer heading font
            heading_font = ("Segoe UI", 9, "bold") 
            self.style.configure("Treeview.Heading", font=heading_font)
        else:
            # For other platforms use a darker theme
            self.style.theme_use('clam')
            
            # Configure colors for dark theme
            self.bg_color = "#2E2E2E"
            self.fg_color = "#FFFFFF"
            self.highlight_color = "#4E4E4E"
            self.accent_color = "#6600CC"
            
        # Configure the style
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TButton', padding=6, background=self.accent_color, foreground=self.fg_color)
        self.style.map('TButton', background=[('active', self.accent_color)])
        
        # Configure Treeview style
        self.style.configure("Treeview", 
                           background=self.bg_color,
                           foreground=self.fg_color,
                           rowheight=25,
                           fieldbackground=self.bg_color)
        self.style.map('Treeview', background=[('selected', self.accent_color)])
        
        # Root configuration
        self.root.configure(bg=self.bg_color)
        
        # SIMPLIFIED LAYOUT - Fix the geometry manager conflict
        # Create main frame with proper padding
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create widgets
        self.create_save_selector()
        self.create_notebook()
        
        # Status bar at the bottom
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Auto-detect saves
        self.save_paths = []
        self.detect_saves()
    
    def create_save_selector(self):
        """Create the save folder selection section."""
        save_frame = ttk.LabelFrame(self.main_frame, text="Save Folder")
        save_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Dropdown for save selection
        save_label = ttk.Label(save_frame, text="Select Save:")
        save_label.grid(row=0, column=0, padx=8, pady=8, sticky=tk.W)
        
        self.save_var = tk.StringVar()
        self.save_combo = ttk.Combobox(save_frame, textvariable=self.save_var, width=50, state="readonly")
        self.save_combo.grid(row=0, column=1, padx=8, pady=8, sticky=tk.W)
        self.save_combo.bind("<<ComboboxSelected>>", self.on_save_selected)
        
        # Browse button
        browse_btn = ttk.Button(save_frame, text="Browse...", command=self.browse_save)
        browse_btn.grid(row=0, column=2, padx=8, pady=8, sticky=tk.W)
        
        # Detect button
        detect_btn = ttk.Button(save_frame, text="Auto-Detect", command=self.detect_saves)
        detect_btn.grid(row=0, column=3, padx=8, pady=8, sticky=tk.W)
        
        # Current save path label
        self.path_var = tk.StringVar()
        path_label = ttk.Label(save_frame, textvariable=self.path_var)
        path_label.grid(row=1, column=0, columnspan=4, padx=8, pady=8, sticky=tk.W)
    
    def create_notebook(self):
        """Create the tabbed interface."""
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.products_tab = ttk.Frame(self.notebook)
        self.rename_tab = ttk.Frame(self.notebook)
        self.bulk_tab = ttk.Frame(self.notebook)
        self.about_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.products_tab, text="Product List")
        self.notebook.add(self.rename_tab, text="Rename")
        self.notebook.add(self.bulk_tab, text="Bulk Rename")
        self.notebook.add(self.about_tab, text="About")
        
        # Set up tabs
        self.setup_products_tab()
        self.setup_rename_tab()
        self.setup_bulk_tab()
        self.setup_about_tab()
    
    def setup_products_tab(self):
        """Set up the products listing tab."""
        # Create a frame for search
        search_frame = ttk.Frame(self.products_tab)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        search_label = ttk.Label(search_frame, text="Filter:")
        search_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_product_list)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        refresh_btn = ttk.Button(search_frame, text="Refresh", command=self.refresh_product_list)
        refresh_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Create a treeview for products
        columns = ("ID", "Name", "Type", "Properties")
        self.product_tree = ttk.Treeview(self.products_tab, columns=columns, show="headings")
        
        # Sort variables
        self.sort_column = "Type"  # Default sort column
        self.sort_reverse = False  # Ascending by default
        
        # Column display text mapping
        self.column_display = {
            "ID": "Product ID",
            "Name": "Display Name", 
            "Type": "Type",
            "Properties": "Properties"
        }
        
        # Set column headings
        for col in columns:
            if col == self.sort_column:
                # Default sort column gets a sort indicator
                direction = " ▲"  # Ascending by default
                self.product_tree.heading(col, text=self.column_display[col] + direction,
                                      command=lambda c=col: self.treeview_sort_column(c))
            else:
                self.product_tree.heading(col, text=self.column_display[col],
                                      command=lambda c=col: self.treeview_sort_column(c))
        
        # Set column widths
        self.product_tree.column("ID", width=150)
        self.product_tree.column("Name", width=200)
        self.product_tree.column("Type", width=150)
        self.product_tree.column("Properties", width=250)
        
        # Add scrollbars
        tree_scroll_y = ttk.Scrollbar(self.products_tab, orient=tk.VERTICAL, command=self.product_tree.yview)
        tree_scroll_x = ttk.Scrollbar(self.products_tab, orient=tk.HORIZONTAL, command=self.product_tree.xview)
        self.product_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        # Place scrollbars and treeview
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.product_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind double-click to open rename tab
        self.product_tree.bind("<Double-1>", self.on_product_double_click)
    
    def treeview_sort_column(self, column):
        """Sort treeview contents when a column is clicked."""
        if self.sort_column == column:
            # If already sorting on this column, reverse the sort direction
            self.sort_reverse = not self.sort_reverse
        else:
            # New sort column
            self.sort_column = column
            self.sort_reverse = False
        
        # Update UI to show sort direction
        for col in ("ID", "Name", "Type", "Properties"):
            # Remove existing sort indicators
            if self.sort_column == col:
                # Add the sort indicator
                direction = " ▼" if self.sort_reverse else " ▲"
                self.product_tree.heading(col, text=self.column_display[col] + direction, 
                                        command=lambda c=col: self.treeview_sort_column(c))
            else:
                # Remove any sort indicator
                self.product_tree.heading(col, text=self.column_display[col],
                                        command=lambda c=col: self.treeview_sort_column(c))
        
        # Get all items
        items = self.product_tree.get_children('')
        
        # Get item values with appropriate data type conversion
        data_list = []
        for item in items:
            value = self.product_tree.set(item, column)
            
            # Convert to appropriate data type for better sorting
            # All values are strings in treeview, need to handle case-insensitive for text
            data_list.append((value.lower() if isinstance(value, str) else value, item))
        
        # Sort the list - case-insensitive for strings
        data_list.sort(reverse=self.sort_reverse)
        
        # Rearrange items in sorted order
        for index, (_, item) in enumerate(data_list):
            self.product_tree.move(item, '', index)
    
    def setup_rename_tab(self):
        """Set up the rename tab."""
        # Create a frame for the rename form
        form_frame = ttk.Frame(self.rename_tab)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Original ID
        id_label = ttk.Label(form_frame, text="Product ID:")
        id_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.orig_id_var = tk.StringVar()
        self.orig_id_combo = ttk.Combobox(form_frame, textvariable=self.orig_id_var, width=30)
        self.orig_id_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.orig_id_combo.bind("<<ComboboxSelected>>", self.on_product_selected)
        
        # Original Name (read-only)
        name_label = ttk.Label(form_frame, text="Current Name:")
        name_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.orig_name_var = tk.StringVar()
        orig_name_entry = ttk.Entry(form_frame, textvariable=self.orig_name_var, width=30, state="readonly")
        orig_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Separator
        ttk.Separator(form_frame, orient=tk.HORIZONTAL).grid(row=2, column=0, columnspan=2, padx=5, pady=10, sticky=tk.EW)
        
        # New Name (will be used for both name and ID)
        new_name_label = ttk.Label(form_frame, text="New Name:")
        new_name_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.new_name_var = tk.StringVar()
        new_name_entry = ttk.Entry(form_frame, textvariable=self.new_name_var, width=30)
        new_name_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Description label
        desc_label = ttk.Label(form_frame, text="(Name will be applied to both display name and ID)", font=("Helvetica", 8, "italic"))
        desc_label.grid(row=4, column=0, columnspan=2, padx=5, pady=2, sticky=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, padx=5, pady=20)
        
        rename_btn = ttk.Button(button_frame, text="Rename", command=self.rename_product)
        rename_btn.pack(side=tk.LEFT, padx=10)
        
        clear_btn = ttk.Button(button_frame, text="Clear Form", command=self.clear_rename_form)
        clear_btn.pack(side=tk.LEFT, padx=10)
    
    def setup_bulk_tab(self):
        """Set up the bulk rename tab."""
        # Instructions label
        instructions = ttk.Label(self.bulk_tab, text="Enter one product per line in the format:\noriginal_id,new_name")
        instructions.pack(padx=10, pady=10, anchor=tk.W)
        
        # Text area for bulk entries
        self.bulk_text = scrolledtext.ScrolledText(self.bulk_tab, wrap=tk.WORD, width=80, height=20)
        self.bulk_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Example text
        example_text = """# Examples of bulk renaming format:
# Format: original_id,new_name
# The ID will be automatically generated from the name

ultramonkey,Super Ultra Monkey
whitelightning,White Lightning Premium
tokyopiss,Tokyo Thunder
strawberrymclovin,McLovin Gold Edition
ogkush,Original Gangster Kush"""
        self.bulk_text.insert(tk.END, example_text)
        
        # Buttons frame
        button_frame = ttk.Frame(self.bulk_tab)
        button_frame.pack(padx=10, pady=10, fill=tk.X)
        
        apply_btn = ttk.Button(button_frame, text="Apply Changes", command=self.apply_bulk_changes)
        apply_btn.pack(side=tk.LEFT, padx=5)
        
        import_btn = ttk.Button(button_frame, text="Import CSV", command=self.import_csv)
        import_btn.pack(side=tk.LEFT, padx=5)
        
        export_btn = ttk.Button(button_frame, text="Export to CSV", command=self.export_csv)
        export_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(button_frame, text="Clear", command=lambda: self.bulk_text.delete(1.0, tk.END))
        clear_btn.pack(side=tk.LEFT, padx=5)
    
    def setup_about_tab(self):
        """Set up the about tab."""
        about_frame = ttk.Frame(self.about_tab)
        about_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(about_frame, text="Schedule 1 Strain Renamer", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)
        
        # Version
        version_label = ttk.Label(about_frame, text="Version 1.0.0")
        version_label.pack(pady=2)
        
        # Description
        desc_text = """A tool to rename drug strains in the game Schedule 1.

This tool allows you to customize your game by changing the names and IDs of drug products. 
It automatically detects save locations and creates backups before making any changes.

Features:
• Rename product display names
• Change product IDs
• Bulk rename multiple products at once
• Filter and search products
• Auto-save detection"""
        
        desc_label = ttk.Label(about_frame, text=desc_text, wraplength=500, justify=tk.CENTER)
        desc_label.pack(pady=10)
        
        # Credits
        credits_label = ttk.Label(about_frame, text="Created for Nexus Mods", font=("Helvetica", 10, "italic"))
        credits_label.pack(pady=10)
        
        # Warning
        warning_text = "IMPORTANT: Always make manual backups of your save files before using this tool."
        warning_label = ttk.Label(about_frame, text=warning_text, foreground="#FF6B6B", wraplength=500, justify=tk.CENTER)
        warning_label.pack(pady=10)
    
    def detect_saves(self):
        """Auto-detect save folders."""
        self.save_paths = find_save_folders()
        
        if not self.save_paths:
            self.status_var.set("No save folders found. Please browse manually.")
            self.save_combo['values'] = ["No saves found"]
            return
        
        self.save_combo['values'] = [save[0] for save in self.save_paths]
        self.save_combo.current(0)
        self.on_save_selected(None)
        self.status_var.set(f"Found {len(self.save_paths)} save folder(s)")
    
    def browse_save(self):
        """Browse for save folder manually."""
        folder = filedialog.askdirectory(title="Select Schedule 1 Save Folder")
        if folder:
            if os.path.exists(os.path.join(folder, "Products.json")):
                # Valid save folder
                save_name = f"Custom: {os.path.basename(os.path.dirname(folder))}/{os.path.basename(folder)}"
                self.save_paths.append((save_name, folder))
                self.save_combo['values'] = [save[0] for save in self.save_paths]
                self.save_combo.set(save_name)
                self.on_save_selected(None)
            else:
                messagebox.showerror("Invalid Save Folder", 
                                     "The selected folder doesn't seem to be a valid Schedule 1 save folder.\n\n"
                                     "Please make sure it contains Products.json file.")
    
    def on_save_selected(self, event):
        """Handle save selection."""
        selected = self.save_var.get()
        
        # Find the path for the selected save
        for save in self.save_paths:
            if save[0] == selected:
                path = save[1]
                self.mod_tool.set_save_path(path)
                self.path_var.set(f"Path: {path}")
                self.refresh_product_list()
                break
    
    def refresh_product_list(self):
        """Refresh the product list."""
        # Clear existing items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        # Update ID combo box
        self.update_id_combo()
            
        # Load products
        if not self.mod_tool.load_products_data():
            self.status_var.set("Failed to load products data")
            return
            
        # Get product details and populate treeview
        products = self.mod_tool.get_product_details()
        
        for product in products:
            # Apply filter if any
            filter_text = self.search_var.get().lower()
            if filter_text and not (filter_text in product["id"].lower() or filter_text in product["name"].lower()):
                continue
                
            # Format properties as comma-separated string
            properties_str = ", ".join(product["properties"]) if product["properties"] else ""
            
            # Add to treeview
            self.product_tree.insert("", tk.END, values=(
                product["id"],
                product["name"],
                product["type"].replace("ProductData", ""),
                properties_str
            ))
        
        # Apply the default sort (by Type)
        self.treeview_sort_column(self.sort_column)
        
        self.status_var.set(f"Loaded {len(products)} products")
    
    def filter_product_list(self, *args):
        """Filter the product list based on search text."""
        self.refresh_product_list()
    
    def update_id_combo(self):
        """Update the product ID combo box."""
        if not self.mod_tool.load_products_data():
            return
            
        products = self.mod_tool.get_product_details()
        product_ids = [p["id"] for p in products]
        
        self.orig_id_combo['values'] = product_ids
        
        # Clear existing selection
        self.orig_id_var.set("")
        self.orig_name_var.set("")
    
    def on_product_selected(self, event):
        """Handle product selection in rename tab."""
        selected_id = self.orig_id_var.get()
        
        if not selected_id:
            return
            
        # Find the product details
        for product in self.mod_tool.get_product_details():
            if product["id"] == selected_id:
                self.orig_name_var.set(product["name"])
                self.new_name_var.set(product["name"])
                break
    
    def on_product_double_click(self, event):
        """Handle double-click on product in the list."""
        # Get the selected item
        item = self.product_tree.selection()[0]
        product_id = self.product_tree.item(item, "values")[0]
        
        # Switch to rename tab and load the product
        self.notebook.select(self.rename_tab)
        self.orig_id_var.set(product_id)
        self.on_product_selected(None)
    
    def clear_rename_form(self):
        """Clear the rename form."""
        self.orig_id_var.set("")
        self.orig_name_var.set("")
        self.new_name_var.set("")
    
    def rename_product(self):
        """Rename a single product by changing both ID and display name."""
        orig_id = self.orig_id_var.get()
        new_name = self.new_name_var.get()
        
        if not orig_id or not new_name:
            messagebox.showerror("Error", "Product ID and new name are required")
            return
        
        # Create a valid ID from the name (lowercase, remove spaces, special chars)
        new_id = re.sub(r'[^a-z0-9]', '', new_name.lower())
        if not new_id:
            messagebox.showerror("Error", "New name must contain some alphanumeric characters")
            return
        
        # Ensure the ID is unique
        if new_id != orig_id and new_id in self.mod_tool.get_product_list():
            # Add a number to make it unique
            base_id = new_id
            counter = 1
            while new_id in self.mod_tool.get_product_list():
                new_id = f"{base_id}{counter}"
                counter += 1
        
        try:
            # Change both ID and name
            if self.mod_tool.change_product_id(orig_id, new_id, new_name):
                messagebox.showinfo("Success", f"Changed product '{orig_id}' to '{new_id}' with name '{new_name}'")
                self.clear_rename_form()
                self.refresh_product_list()
            else:
                messagebox.showerror("Error", "Failed to rename product")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def apply_bulk_changes(self):
        """Apply bulk changes from text area."""
        text = self.bulk_text.get(1.0, tk.END)
        lines = text.strip().split("\n")
        
        # Get current product list for ID collision checking
        product_list = self.mod_tool.get_product_list()
        
        # Track new IDs that will be created during this batch to avoid collisions
        new_ids_in_batch = set()
        
        rename_list = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
                
            parts = [part.strip() for part in line.split(",")]
            if len(parts) < 2:
                continue
                
            old_id = parts[0]
            new_name = parts[1]
            
            # Create a valid ID from the name (lowercase, remove spaces, special chars)
            new_id = re.sub(r'[^a-z0-9]', '', new_name.lower())
            if not new_id:
                # Skip entries that would generate invalid IDs
                messagebox.showwarning("Warning", f"Skipping '{old_id}' - new name '{new_name}' would generate an invalid ID")
                continue
            
            # Ensure the new ID is unique (both in database and current batch)
            if new_id != old_id and (new_id in product_list or new_id in new_ids_in_batch):
                # Add a number to make it unique
                base_id = new_id
                counter = 1
                while new_id in product_list or new_id in new_ids_in_batch:
                    new_id = f"{base_id}{counter}"
                    counter += 1
            
            # Track this new ID to avoid collisions in the same batch
            new_ids_in_batch.add(new_id)
            
            # Add to rename list with auto-generated ID
            rename_list.append((old_id, new_id, new_name))
        
        if not rename_list:
            messagebox.showinfo("Info", "No valid rename entries found")
            return
            
        # Confirm with user
        confirm = messagebox.askyesno("Confirm Bulk Rename", 
                                     f"This will rename {len(rename_list)} products.\n\n"
                                     "A backup will be created automatically.\n\n"
                                     "Proceed?")
        if not confirm:
            return
            
        try:
            success, errors = self.mod_tool.bulk_rename_from_list(rename_list)
            if errors == 0:
                messagebox.showinfo("Success", f"Successfully renamed {success} products")
            else:
                messagebox.showwarning("Partial Success", 
                                     f"Renamed {success} products successfully\n"
                                     f"Failed to rename {errors} products")
            
            self.refresh_product_list()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def import_csv(self):
        """Import a CSV file for bulk rename."""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Clear and set text
            self.bulk_text.delete(1.0, tk.END)
            self.bulk_text.insert(tk.END, content)
            
            self.status_var.set(f"Imported {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import file: {str(e)}")
    
    def export_csv(self):
        """Export the bulk rename text to a CSV file."""
        file_path = filedialog.asksaveasfilename(
            title="Save CSV File",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            content = self.bulk_text.get(1.0, tk.END)
            
            with open(file_path, 'w') as f:
                f.write(content)
                
            self.status_var.set(f"Exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export file: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScheduleGUI(root)
    root.mainloop() 