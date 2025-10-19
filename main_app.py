# file: main_app.py

import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import networkx as nx

from database_manager import DatabaseManager
from graph_manager import GraphManager

class CityMapNavigatorApp(tk.Tk):
    """The main GUI application for the City Map Navigator."""

    def __init__(self):
        super().__init__()
        self.title("Graph-Based City Map Navigator")
        self.geometry("1200x800")

        self.db_manager = DatabaseManager()
        self.graph_manager = GraphManager()
        self.picked_node = None # To track the currently dragged node

        self._load_initial_graph()
        self._create_widgets()
        self._draw_graph()
        self._connect_mpl_events() # Connect mouse events

        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _load_initial_graph(self):
        self.graph_manager.load_graph_from_db(self.db_manager)

    def _create_widgets(self):
        # ... (This entire method remains unchanged) ...
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        control_frame = ttk.Frame(main_pane, width=350, relief=tk.RIDGE)
        main_pane.add(control_frame, weight=1)
        
        graph_frame = ttk.Frame(main_pane, relief=tk.SUNKEN)
        main_pane.add(graph_frame, weight=4)

        path_frame = ttk.LabelFrame(control_frame, text="Find Shortest Path")
        path_frame.pack(padx=10, pady=10, fill=tk.X)

        ttk.Label(path_frame, text="Start Location:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.start_var = tk.StringVar()
        self.start_combo = ttk.Combobox(path_frame, textvariable=self.start_var, state="readonly")
        self.start_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(path_frame, text="End Location:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.end_var = tk.StringVar()
        self.end_combo = ttk.Combobox(path_frame, textvariable=self.end_var, state="readonly")
        self.end_combo.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(path_frame, text="Find Path", command=self._find_path_action).grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(path_frame, text="Clear Path", command=self._clear_path_action).grid(row=3, column=0, columnspan=2, pady=5)

        add_frame = ttk.LabelFrame(control_frame, text="Add Data to Map")
        add_frame.pack(padx=10, pady=10, fill=tk.X)

        ttk.Label(add_frame, text="Name:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.loc_name_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.loc_name_var).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(add_frame, text="Coord X:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.loc_x_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.loc_x_var).grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(add_frame, text="Coord Y:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.loc_y_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.loc_y_var).grid(row=2, column=1, padx=5, pady=2)

        ttk.Button(add_frame, text="Add Location", command=self._add_location_action).grid(row=3, column=0, columnspan=2, pady=5)
        ttk.Separator(add_frame, orient=tk.HORIZONTAL).grid(row=4, columnspan=2, sticky='ew', pady=10)
        
        ttk.Label(add_frame, text="From:").grid(row=5, column=0, padx=5, pady=2, sticky="w")
        self.road_start_var = tk.StringVar()
        self.road_start_combo = ttk.Combobox(add_frame, textvariable=self.road_start_var, state="readonly")
        self.road_start_combo.grid(row=5, column=1, padx=5, pady=2)

        ttk.Label(add_frame, text="To:").grid(row=6, column=0, padx=5, pady=2, sticky="w")
        self.road_end_var = tk.StringVar()
        self.road_end_combo = ttk.Combobox(add_frame, textvariable=self.road_end_var, state="readonly")
        self.road_end_combo.grid(row=6, column=1, padx=5, pady=2)

        ttk.Label(add_frame, text="Distance/Weight:").grid(row=7, column=0, padx=5, pady=2, sticky="w")
        self.road_weight_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.road_weight_var).grid(row=7, column=1, padx=5, pady=2)
        
        ttk.Button(add_frame, text="Add Road", command=self._add_road_action).grid(row=8, column=0, columnspan=2, pady=5)
        
        delete_frame = ttk.LabelFrame(control_frame, text="Delete Data from Map")
        delete_frame.pack(padx=10, pady=10, fill=tk.X)

        ttk.Label(delete_frame, text="Location:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.delete_loc_var = tk.StringVar()
        self.delete_loc_combo = ttk.Combobox(delete_frame, textvariable=self.delete_loc_var, state="readonly")
        self.delete_loc_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(delete_frame, text="Delete Location", command=self._delete_location_action).grid(row=1, column=0, columnspan=2, pady=5)

        view_export_frame = ttk.LabelFrame(control_frame, text="View & Export")
        view_export_frame.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Button(view_export_frame, text="View Adjacency Matrix", command=self._view_adjacency_matrix).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(view_export_frame, text="View Incidence Matrix", command=self._view_incidence_matrix).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(view_export_frame, text="Export to JSON", command=self._export_json).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(view_export_frame, text="Export to CSV", command=self._export_csv).pack(fill=tk.X, padx=5, pady=2)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(control_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w").pack(side=tk.BOTTOM, fill=tk.X)

        self.fig = plt.figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, graph_frame)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self._update_comboboxes()
        
    def _update_comboboxes(self):
        locations = self.graph_manager.get_node_names()
        self.start_combo['values'] = locations
        self.end_combo['values'] = locations
        self.road_start_combo['values'] = locations
        self.road_end_combo['values'] = locations
        self.delete_loc_combo['values'] = locations

    def _draw_graph(self, highlight_path=None):
        # ... (This method remains unchanged) ...
        self.ax.clear()
        G = self.graph_manager.graph
        pos = nx.get_node_attributes(G, 'pos')
        
        if not pos:
            self.ax.text(0.5, 0.5, "Map is empty. Add locations and roads.", ha='center', va='center')
            self.canvas.draw()
            return
            
        nx.draw_networkx_nodes(G, pos, ax=self.ax, node_color='skyblue', node_size=500)
        nx.draw_networkx_edges(G, pos, ax=self.ax, edge_color='gray')
        nx.draw_networkx_labels(G, pos, ax=self.ax, font_size=8)
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=self.ax, font_size=7)

        if highlight_path:
            path_edges = list(zip(highlight_path, highlight_path[1:]))
            nx.draw_networkx_nodes(G, pos, nodelist=highlight_path, node_color='lightgreen', node_size=600, ax=self.ax)
            nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=2, ax=self.ax)
        
        self.ax.set_title("City Map")
        self.ax.axis('off')
        self.fig.tight_layout()
        self.canvas.draw()

    # <<< START OF ADDED/MODIFIED CODE >>>

    def _connect_mpl_events(self):
        """Connects matplotlib mouse events to handler functions."""
        self.canvas.mpl_connect('button_press_event', self._on_press)
        self.canvas.mpl_connect('motion_notify_event', self._on_motion)
        self.canvas.mpl_connect('button_release_event', self._on_release)

    def _on_press(self, event):
        """Handles the mouse button press event to pick up a node."""
        if event.inaxes != self.ax:
            return
        
        G = self.graph_manager.graph
        pos = nx.get_node_attributes(G, 'pos')
        if not pos: return

        # Find the node closest to the click event
        node_clicked, min_dist = None, float('inf')
        for node, (x, y) in pos.items():
            dist = ((event.xdata - x)**2 + (event.ydata - y)**2)**0.5
            if dist < min_dist:
                node_clicked, min_dist = node, dist
        
        # Set a threshold to determine if the click is close enough to a node
        click_radius_threshold = 20
        if min_dist < click_radius_threshold:
            self.picked_node = node_clicked
            self.status_var.set(f"Dragging '{self.picked_node}'...")

    def _on_motion(self, event):
        """Handles mouse movement to drag the picked node."""
        if self.picked_node is None or event.inaxes != self.ax:
            return

        # Update the node's position in the in-memory graph
        new_pos = (event.xdata, event.ydata)
        self.graph_manager.graph.nodes[self.picked_node]['pos'] = new_pos
        
        # Redraw the graph to show the node moving in real-time
        self._draw_graph()

    def _on_release(self, event):
        """Handles the mouse button release to place the node and save its new position."""
        if self.picked_node is None:
            return

        # Get the final coordinates from the graph object
        final_pos = self.graph_manager.graph.nodes[self.picked_node]['pos']
        final_x, final_y = int(final_pos[0]), int(final_pos[1])

        # Update the coordinates in the database
        if self.db_manager.update_location_coords(self.picked_node, final_x, final_y):
            self.status_var.set(f"Updated '{self.picked_node}' position to ({final_x}, {final_y}).")
        else:
            self.status_var.set(f"Error updating position for '{self.picked_node}'.")
            # If the database update fails, reload from DB to revert the visual change
            self.graph_manager.load_graph_from_db(self.db_manager)
            self._draw_graph()
        
        # Reset the picked node state
        self.picked_node = None

    # <<< END OF ADDED/MODIFIED CODE >>>

    # ... (All other methods like _find_path_action, _add_location_action, etc., remain unchanged) ...
    def _find_path_action(self):
        start, end = self.start_var.get(), self.end_var.get()
        if not start or not end:
            messagebox.showerror("Error", "Please select both a start and end location.")
            return
        if start == end:
            messagebox.showinfo("Info", "Start and end locations are the same.")
            self._draw_graph(highlight_path=[start])
            return
        path = self.graph_manager.find_shortest_path(start, end)
        if path:
            self._draw_graph(highlight_path=path)
            self.status_var.set(f"Shortest path: {' -> '.join(path)}")
        else:
            messagebox.showerror("Error", f"No path found between {start} and {end}.")
            self.status_var.set(f"No path found between {start} and {end}.")
            self._draw_graph()

    def _clear_path_action(self):
        self.start_var.set('')
        self.end_var.set('')
        self._draw_graph()
        self.status_var.set("Path cleared. Ready.")
            
    def _add_location_action(self):
        name = self.loc_name_var.get()
        try:
            x, y = int(self.loc_x_var.get()), int(self.loc_y_var.get())
        except ValueError:
            messagebox.showerror("Error", "Coordinates X and Y must be integers.")
            return
        if not name:
            messagebox.showerror("Error", "Location name cannot be empty.")
            return
        if self.db_manager.add_location(name, x, y):
            self.status_var.set(f"Location '{name}' added successfully.")
            self.graph_manager.load_graph_from_db(self.db_manager)
            self._update_comboboxes()
            self._draw_graph()
            self.loc_name_var.set(""), self.loc_x_var.set(""), self.loc_y_var.set("")
        else:
            messagebox.showerror("Error", f"Location '{name}' could not be added. It may already exist.")
            self.status_var.set(f"Failed to add location '{name}'.")

    def _add_road_action(self):
        start, end = self.road_start_var.get(), self.road_end_var.get()
        try:
            weight = float(self.road_weight_var.get())
        except ValueError:
            messagebox.showerror("Error", "Weight must be a valid number.")
            return
        if not all([start, end]):
            messagebox.showerror("Error", "Please select 'From' and 'To' locations.")
            return
        if self.db_manager.add_road(start, end, weight):
            self.status_var.set(f"Road between '{start}' and '{end}' added.")
            self.graph_manager.load_graph_from_db(self.db_manager)
            self._draw_graph()
            self.road_weight_var.set("")
        else:
            messagebox.showerror("Error", "Could not add the road.")

    def _delete_location_action(self):
        name_to_delete = self.delete_loc_var.get()
        if not name_to_delete:
            messagebox.showerror("Error", "Please select a location to delete.")
            return

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{name_to_delete}'? This will also remove all connected roads."):
            if self.db_manager.delete_location(name_to_delete):
                self.status_var.set(f"Location '{name_to_delete}' deleted successfully.")
                self.graph_manager.load_graph_from_db(self.db_manager)
                self._update_comboboxes()
                self._draw_graph()
                self.delete_loc_var.set('')
            else:
                messagebox.showerror("Error", f"Failed to delete '{name_to_delete}'. Check logs for details.")
                self.status_var.set(f"Failed to delete location '{name_to_delete}'.")
    
    def _view_adjacency_matrix(self):
        adj_matrix, _ = self.graph_manager.get_adjacency_matrix()
        # Corrected the typo from adj_ to adj_matrix and removed unnecessary transpose .T
        self._show_matrix_in_new_window(adj_matrix, "Adjacency Matrix")

    def _view_incidence_matrix(self):
        inc_matrix, _, _ = self.graph_manager.get_incidence_matrix()
        self._show_matrix_in_new_window(inc_matrix, "Incidence Matrix")
        
    def _show_matrix_in_new_window(self, matrix_df, title):
        if matrix_df.empty:
            messagebox.showinfo("Info", "The graph is empty. Cannot generate matrix.")
            return
        win = Toplevel(self); win.title(title); win.geometry("600x400")
        frame = ttk.Frame(win); frame.pack(expand=True, fill='both')
        tree = ttk.Treeview(frame, show="headings")
        tree["columns"] = ["#0"] + list(matrix_df.columns)
        tree.column("#0", width=100, anchor='w'); tree.heading("#0", text="Node")
        for col in matrix_df.columns:
            tree.column(col, width=80, anchor='center'); tree.heading(col, text=str(col))
        for index, row in matrix_df.iterrows():
            tree.insert("", "end", text=index, values=[index] + list(row))
        ysb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        xsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        ysb.pack(side='right', fill='y'); xsb.pack(side='bottom', fill='x'); tree.pack(side='left', expand=True, fill='both')

    def _export_json(self):
        self.graph_manager.export_to_json()
        messagebox.showinfo("Export Success", "Graph data exported to 'graph_data.json'.")
        self.status_var.set("Exported to JSON.")
        
    def _export_csv(self):
        self.graph_manager.export_to_csv()
        messagebox.showinfo("Export Success", "Graph data exported to 'nodes.csv' and 'edges.csv'.")
        self.status_var.set("Exported to CSV.")

    def _on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to exit the application?"):
            self.db_manager.close()
            self.destroy()

if __name__ == "__main__":
    db = DatabaseManager()
    if not db.get_all_locations():
        from database_manager import populate_initial_data
        populate_initial_data(db)
    db.close()
    
    app = CityMapNavigatorApp()
    app.mainloop()