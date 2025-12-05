# Workshop Exercise Structure

This workshop provides a progressive learning experience through three difficulty levels: **Blue** (Easy), **Red** (Intermediate), and **Black** (Advanced).

## Exercise Nomenclature

Each exercise is identified by a label that indicates both its **location** and **difficulty level**.

### Prefix - File Location

- **WS_#** = Workshop Student exercises in `pa_app_main.py` (main GUI file)
- **WK_#** = Workshop exercises in `pa_app_thread.py` (worker thread file)

### Suffix - Difficulty Level

- **No suffix** (WS, WK) = Core exercises present in **all three levels** (Blue, Red, Black)
- **R suffix** (WSR, WKR) = Red-level exercises present in **Red and Black only**
- **B suffix** (WSB, WKB) = Black-level exercises present in **Black only**

### Examples

- `WS_1` - Core exercise in main file (appears in Blue, Red, and Black)
- `WSR_5` - Red-level exercise in main file (appears in Red and Black)
- `WSB_2` - Black-level exercise in main file (appears in Black only)
- `WK_7` - Core exercise in thread file (appears in Blue, Red, and Black)
- `WKR_3` - Red-level exercise in thread file (appears in Red and Black)
- `WKB_1` - Black-level exercise in thread file (appears in Black only)

## Difficulty Levels

### Blue (Easy) - 22 exercises
**Files:** `blue/pa_app_main.py`, `blue/pa_app_thread.py`

**UI Tasks:** Complete UI provided - students focus on Python code only

**Exercise Types:**
- WS_1-4: Core main file exercises
- WK_1-18: Core thread file exercises

**Skill Focus:** Basic PyQt6, SCPI commands, threading fundamentals

---

### Red (Intermediate) - 41 exercises
**Files:** `red/pa_app_main.py`, `red/pa_app_thread.py`

**UI Tasks:** Students add basic widgets:
1. QDial widget named "dial" for power control
2. QLabel widget named "label_18" to display dial value
3. Connect dial's valueChanged signal to label_18's setNum slot

**Exercise Types:**
- WS_1-4: Core main file exercises
- WSR_1-14: Red-specific main file exercises
- WK_1-18: Core thread file exercises
- WKR_1-5: Red-specific thread file exercises

**Skill Focus:** UI design basics, resource management, signal/slot connections, plot widgets

---

### Black (Advanced) - 51 exercises
**Files:** `black/pa_app_main.py`, `black/pa_app_thread.py`

**UI Tasks:** Students add extensive widgets:
1. QDial widget named "dial" for power control
2. QLabel widget named "label_18" to display dial value
3. Connect dial's valueChanged signal to label_18's setNum slot
4. QLineEdit widgets: lineEdit_3 (Fstart), lineEdit_4 (Fstop), lineEdit_5 (Npoints)
5. QLCDNumber widgets: lcdNumber (Gain), lcdNumber_2 (OP1dB), lcdNumber_3 (OIP3), lcdNumber_4 (OIP5), lcdNumber_5 (Pout)
6. QPushButton named "pushButton_2" for Test PA

**Exercise Types:**
- WS_1-4: Core main file exercises
- WSR_1-14: Red-specific main file exercises
- WSB_1-7: Black-specific main file exercises
- WK_1-18: Core thread file exercises
- WKR_1-5: Red-specific thread file exercises
- WKB_1-2: Black-specific thread file exercises

**Skill Focus:** Complete application development, complex UI design, h_gui dictionary management, callback functions

## Exercise Reference Files

Each level has a corresponding CSV file containing exercise details:

- `blue_exercises.csv` - 22 exercises
- `red_exercises.csv` - 41 exercises
- `black_exercises.csv` - 51 exercises

### CSV Format

Each CSV contains the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `label` | Exercise designator | WSR_1, WK_8 |
| `todo` | Task description | "Import everything you need" |
| `reference_slide` | Slide number reference | 2-54, 4-27 |
| `reference_exercise` | Example exercise number | 109, 310 |

## Progressive Learning Path

The workshop is designed for progressive skill building:

1. **Start with Blue** if you're new to PyQt6 and SCPI programming
   - Complete UI provided
   - Focus on understanding the code flow
   - 22 focused exercises

2. **Move to Red** once comfortable with basics
   - Add simple UI elements using Qt Designer
   - Implement resource management
   - 41 total exercises (includes all Blue exercises + 19 new)

3. **Challenge yourself with Black** for full application development
   - Design complex UI with multiple widget types
   - Implement complete h_gui dictionary
   - 51 total exercises (includes all Red exercises + 10 new)

## File Structure

```
workshop/
├── README.md                  # This file
├── blue/
│   ├── pa_app.ui             # Complete UI file
│   ├── pa_app_main.py        # Main application (WS exercises)
│   └── pa_app_thread.py      # Worker thread (WK exercises)
├── blue_exercises.csv        # Blue exercise reference
├── red/
│   ├── pa_app.ui             # Partial UI (students add widgets)
│   ├── pa_app_main.py        # Main application (WS + WSR exercises)
│   └── pa_app_thread.py      # Worker thread (WK + WKR exercises)
├── red_exercises.csv         # Red exercise reference
├── black/
│   ├── pa_app.ui             # Minimal UI (students add many widgets)
│   ├── pa_app_main.py        # Main application (WS + WSR + WSB exercises)
│   └── pa_app_thread.py      # Worker thread (WK + WKR + WKB exercises)
├── black_exercises.csv       # Black exercise reference
└── solution/                 # Complete working solution
    ├── pa_app.ui
    ├── pa_app_solution.py
    └── pa_app_thread.py
```

## Getting Started

1. Choose your difficulty level based on your experience
2. Open the CSV file for your chosen level to see all exercises
3. Open `pa_app.ui` in Qt Designer (if required for your level)
4. Complete the UI tasks (Red and Black levels)
5. Work through the Python exercises in order
6. Reference the solution folder if you get stuck

## Tips for Success

- **Read the CSV file first** - Understanding all exercises helps you see the big picture
- **Complete exercises in order** - Later exercises often depend on earlier ones
- **Check slide references** - The referenced slides contain helpful examples
- **Test frequently** - Run your code after completing each major section
- **Use Qt Designer** - For Red and Black levels, complete UI tasks before coding
- **Refer to solution code** - The solution folder contains working implementations

## Questions or Issues?

If you encounter problems or have questions about the exercises, refer to:
- The solution code in `workshop/solution/`
- The slide deck references in the CSV files
- The example exercises referenced in the CSV files
