# file: database_manager.py

import sqlite3

class DatabaseManager:
    """A class to manage the SQLite database for the city map."""
    
    def __init__(self, db_name='city_map.db'):
        """Initializes the database connection and creates tables if they don't exist."""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Creates the 'locations' and 'roads' tables."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                x INTEGER NOT NULL,
                y INTEGER NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS roads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_location_id INTEGER,
                end_location_id INTEGER,
                weight REAL NOT NULL,
                FOREIGN KEY (start_location_id) REFERENCES locations(id),
                FOREIGN KEY (end_location_id) REFERENCES locations(id)
            )
        ''')
        self.conn.commit()

    def add_location(self, name: str, x: int, y: int) -> bool:
        """Adds a new location (node) to the database."""
        try:
            self.cursor.execute("INSERT INTO locations (name, x, y) VALUES (?, ?, ?)", (name, x, y))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"Error: Location '{name}' already exists.")
            return False

    def add_road(self, start_name: str, end_name: str, weight: float) -> bool:
        """Adds a new road (edge) between two locations."""
        try:
            start_id = self._get_location_id(start_name)
            end_id = self._get_location_id(end_name)
            if start_id is not None and end_id is not None:
                self.cursor.execute(
                    "INSERT INTO roads (start_location_id, end_location_id, weight) VALUES (?, ?, ?)",
                    (start_id, end_id, weight)
                )
                self.cursor.execute(
                    "INSERT INTO roads (start_location_id, end_location_id, weight) VALUES (?, ?, ?)",
                    (end_id, start_id, weight)
                )
                self.conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Error adding road: {e}")
            return False
            
    def _get_location_id(self, name: str) -> int | None:
        """Retrieves the ID of a location by its name."""
        self.cursor.execute("SELECT id FROM locations WHERE name = ?", (name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def delete_location(self, name: str) -> bool:
        """Deletes a location and all associated roads from the database."""
        location_id = self._get_location_id(name)
        if location_id is None:
            print(f"Error: Location '{name}' not found.")
            return False
        try:
            self.cursor.execute(
                "DELETE FROM roads WHERE start_location_id = ? OR end_location_id = ?",
                (location_id, location_id)
            )
            self.cursor.execute("DELETE FROM locations WHERE id = ?", (location_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting location '{name}': {e}")
            self.conn.rollback()
            return False
    
    # <<< START OF ADDED CODE >>>
    def update_location_coords(self, name: str, x: int, y: int) -> bool:
        """Updates the coordinates of an existing location."""
        try:
            self.cursor.execute("UPDATE locations SET x = ?, y = ? WHERE name = ?", (x, y, name))
            self.conn.commit()
            # Check if a row was actually updated
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating coordinates for '{name}': {e}")
            self.conn.rollback()
            return False
    # <<< END OF ADDED CODE >>>

    def get_all_locations(self) -> list:
        """Fetches all locations from the database."""
        self.cursor.execute("SELECT name, x, y FROM locations")
        return self.cursor.fetchall()

    def get_all_roads(self) -> list:
        """Fetches all roads from the database."""
        self.cursor.execute('''
            SELECT l1.name, l2.name, r.weight 
            FROM roads r
            JOIN locations l1 ON r.start_location_id = l1.id
            JOIN locations l2 ON r.end_location_id = l2.id
        ''')
        return self.cursor.fetchall()

    def close(self):
        """Closes the database connection."""
        self.conn.close()

# The rest of the file remains the same...
def populate_initial_data(db_manager):
    print("Populating database with Indian cities along NH48...")
    locations = [('Delhi', 400, 50), ('Jaipur', 350, 200), ('Udaipur', 300, 350), ('Ahmedabad', 200, 450), ('Mumbai', 150, 650), ('Pune', 250, 700), ('Bengaluru', 450, 850), ('Chennai', 650, 800)]
    roads = [('Delhi', 'Jaipur', 270), ('Jaipur', 'Udaipur', 400), ('Udaipur', 'Ahmedabad', 260), ('Ahmedabad', 'Mumbai', 525), ('Mumbai', 'Pune', 150), ('Pune', 'Bengaluru', 840), ('Bengaluru', 'Chennai', 350)]
    for loc in locations: db_manager.add_location(*loc)
    for road in roads: db_manager.add_road(*road)
    print("Population complete.")

if __name__ == '__main__':
    db = DatabaseManager()
    if not db.get_all_locations(): populate_initial_data(db)
    else: print("Database already contains data.")
    db.close()