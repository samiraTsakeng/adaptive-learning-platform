from ..database import connect_db


def insert_sample_data():
    conn = connect_db()
    cursor = conn.cursor()

    # ----- Courses -----
    cursor.execute("INSERT OR IGNORE INTO courses (id, title, description) VALUES (1, 'Python Basics', 'Introduction to Python')")
    cursor.execute("INSERT OR IGNORE INTO courses (id, title, description) VALUES (2, 'Mathematics', 'Fundamental math topics')")
    cursor.execute("INSERT OR IGNORE INTO courses (id, title, description) VALUES (3, 'Chemistry', 'Introductory chemistry')")
    cursor.execute("INSERT OR IGNORE INTO courses (id, title, description) VALUES (4, 'Database Systems', 'Relational databases and SQL')")
    cursor.execute("INSERT OR IGNORE INTO courses (id, title, description) VALUES (5, 'Computer Science', 'Core Computer Science concepts')")

    # ----- Python Lessons (course_id = 1) -----
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (1, 1, 'Variables', 'Learn variables in Python', 1)")
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (2, 1, 'Loops', 'Learn loops in Python', 2)")
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (3, 1, 'Functions', 'Defining and calling functions', 2)")
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (4, 1, 'Data Types', 'Strings, lists, tuples, dicts', 2)")
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (5, 1, 'File I/O', 'Reading and writing files', 2)")

    # ----- Math Lessons (course_id = 2) - 5 lessons -----
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (6, 2, 'Addition and Subtraction', 'Basic addition and subtraction', 1)")
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (7, 2, 'Multiplication', 'Basic multiplication concepts', 1)")
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (8, 2, 'Division and Modulus', 'Division and modulus operator', 2)")
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (9, 2, 'Fractions', 'Introduction to fractions', 2)")
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (10, 2, 'Word Problems', 'Apply math to problems', 3)")

    # ----- Chemistry Lessons (course_id = 3) - 5 lessons -----
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (11, 3, 'Atoms and Elements', 'Basics of atoms and periodic table', 1)")
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (12, 3, 'Chemical Bonds', 'Ionic and covalent bonds', 2)")
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (13, 3, 'Chemical Reactions', 'Balancing reactions and types', 2)")
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (14, 3, 'Solutions', 'Mixtures and concentrations', 2)")
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (15, 3, 'Acids and Bases', 'pH and properties', 3)")

    # ----- Database Lessons (course_id = 4) - 5 lessons -----
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (16, 4, 'Relational Model', 'Tables, rows, and columns', 1)")
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (17, 4, 'SQL Basics', 'SELECT, FROM, WHERE', 1)")
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (18, 4, 'Joins', 'INNER, LEFT, RIGHT joins', 2)")
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (19, 4, 'Normalization', 'Designing normalized schemas', 3)")
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (20, 4, 'Transactions', 'ACID properties and locking', 3)")

    # ----- Computer Science Lessons (course_id = 5) - 5 lessons -----
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (21, 5, 'Algorithms', 'Basic algorithmic thinking', 2)")
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (22, 5, 'Data Structures', 'Lists, stacks, queues', 2)")
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (23, 5, 'Complexity', 'Time and space complexity', 3)")
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (24, 5, 'Programming Paradigms', 'Procedural vs OOP vs functional', 2)")
    cursor.execute("INSERT OR IGNORE INTO lessons (id, course_id, title, content, difficulty) VALUES (25, 5, 'Computer Architecture', 'CPU, memory hierarchy', 3)")

    # ----- Quizzes: one per lesson (existing lessons 1..22) -----
    for qid, lid in enumerate(range(1, 23), start=1):
        cursor.execute("INSERT OR IGNORE INTO quizzes (id, lesson_id) VALUES (?, ?)", (qid, lid))
    # Quizzes for newly added Python lessons (23..25)
    cursor.execute("INSERT OR IGNORE INTO quizzes (id, lesson_id) VALUES (23, 23)")
    cursor.execute("INSERT OR IGNORE INTO quizzes (id, lesson_id) VALUES (24, 24)")
    cursor.execute("INSERT OR IGNORE INTO quizzes (id, lesson_id) VALUES (25, 25)")

    # ----- Quiz Questions -----
    # Note: questions are inserted below from the `questions` mapping.

    # Explicit questions for each quiz (quiz_id == lesson_id for 1..25)
    questions = {
        # Python (lessons 1..5)
        1: [
            ("What symbol is used for assignment in Python?", "="),
            ("How do you start a comment in Python?", "#"),
            ("Which keyword defines a function?", "def"),
            ("What data type holds True/False?", "bool"),
            ("How do you create a list literal?", "[]"),
        ],
        2: [
            ("Which loop repeats until a condition becomes False?", "while"),
            ("Which loop iterates over items in a sequence?", "for"),
            ("Which statement exits the current loop?", "break"),
            ("Which statement skips to the next loop iteration?", "continue"),
            ("How do you loop over numbers 0..4 using range?", "for i in range(5):"),
        ],
        3: [
            ("Which keyword is used to return a value from a function?", "return"),
            ("How do you define a function that takes two parameters?", "def f(a, b):"),
            ("What built-in allows you to see a function's docstring?", "help"),
            ("What term describes a function defined inside another function?", "nested function"),
            ("How do you call a function named 'foo'?", "foo()"),
        ],
        4: [
            ("Which type is an ordered, mutable sequence?", "list"),
            ("Which type is immutable and ordered like a list?", "tuple"),
            ("Which type stores key/value pairs?", "dict"),
            ("Which method uppercases a string 's'?", "s.upper()"),
            ("How do you get the length of a list 'L'?", "len(L)"),
        ],
        5: [
            ("Which function opens a file in Python?", "open"),
            ("Which mode opens a file for writing, erasing existing content?", "w"),
            ("Which method reads the entire file into a string?", "read()"),
            ("Which statement ensures a file is closed automatically?", "with open(...) as f:"),
            ("Which method writes text to a file object 'f'?", "f.write()"),
        ],

        # Mathematics (lessons 6..10)
        6: [
            ("What is 7 + 5?", "12"),
            ("What is 10 - 4?", "6"),
            ("What is the sum of 3 and 9?", "12"),
            ("If a=2 and b=3, what is a+b?", "5"),
            ("What is 0 + 0?", "0"),
        ],
        7: [
            ("What is 6 × 7?", "42"),
            ("Multiplication is which property: commutative or not?", "commutative"),
            ("What is 5 × 0?", "0"),
            ("What is 9 × 3?", "27"),
            ("If 4×x=20, x=?", "5"),
        ],
        8: [
            ("What is 7 ÷ 2 (integer division result)?", "3"),
            ("What is 7 % 2 (modulus)?", "1"),
            ("What operator gives the remainder of division?", "%"),
            ("What is 10 ÷ 5?", "2"),
            ("What is 14 % 7?", "0"),
        ],
        9: [
            ("In a fraction 3/4, what is the numerator?", "3"),
            ("In 3/4, what is the denominator?", "4"),
            ("What is 1/2 + 1/4?", "3/4"),
            ("Which fraction equals 0.5?", "1/2"),
            ("How do you simplify 2/4?", "1/2"),
        ],
        10: [
            ("If John has 3 apples and gets 2 more, how many?", "5"),
            ("Translate: 'twice a number x'", "2*x"),
            ("If 2x + 3 = 7, what is x?", "2"),
            ("If a rectangle has width 3 and height 4, area?", "12"),
            ("What operation reverses multiplication?", "division"),
        ],

        # Chemistry (lessons 11..15)
        11: [
            ("Which particle has a positive charge in an atom?", "proton"),
            ("Which particle has no charge?", "neutron"),
            ("Which particle orbits the nucleus?", "electron"),
            ("What defines an element?", "number of protons"),
            ("What is the chemical symbol for water?", "H2O"),
        ],
        12: [
            ("Which type of bond involves transfer of electrons?", "ionic"),
            ("Which bond involves sharing electrons?", "covalent"),
            ("Which bond is typically stronger: ionic or hydrogen?", "ionic"),
            ("What forms between Na and Cl?", "ionic bond"),
            ("Which bond often forms molecules like O2?", "covalent"),
        ],
        13: [
            ("In a chemical equation, reactants are on which side?", "left"),
            ("What must be balanced in a chemical reaction?", "atoms"),
            ("What is produced in combustion of hydrocarbons?", "CO2 and H2O"),
            ("What law requires conservation of mass in reactions?", "conservation of mass"),
            ("What is the term for a substance that speeds a reaction?", "catalyst"),
        ],
        14: [
            ("What is the substance dissolved in a solution called?", "solute"),
            ("What is the substance that dissolves the solute?", "solvent"),
            ("What describes amount of solute per volume?", "concentration"),
            ("What unit measures concentration in mol/L?", "molarity"),
            ("Salt dissolved in water makes what type of mixture?", "solution"),
        ],
        15: [
            ("What value measures acidity/basicity?", "pH"),
            ("Which has pH < 7: acid or base?", "acid"),
            ("Which has pH > 7?", "base"),
            ("What ion do acids donate?", "H+"),
            ("What ion do bases produce in water?", "OH-"),
        ],

        # Database (lessons 16..20)
        16: [
            ("What is a table row commonly called?", "record"),
            ("What is a table column commonly called?", "field"),
            ("What uniquely identifies a row?", "primary key"),
            ("What stores structured data in a relational DB?", "table"),
            ("What organizes tables into relations?", "relational model"),
        ],
        17: [
            ("Which clause selects columns in SQL?", "SELECT"),
            ("Which clause specifies the table?", "FROM"),
            ("Which clause filters rows?", "WHERE"),
            ("How do you select all columns?", "SELECT *"),
            ("Which keyword orders results?", "ORDER BY"),
        ],
        18: [
            ("Which JOIN returns rows matching in both tables?", "INNER JOIN"),
            ("Which JOIN returns all rows from left table?", "LEFT JOIN"),
            ("Which JOIN returns all rows from right table?", "RIGHT JOIN"),
            ("Which clause specifies join condition?", "ON"),
            ("What combines rows from two tables?", "join"),
        ],
        19: [
            ("What does 1NF require about columns?", "atomic values"),
            ("What is the process of organizing tables to reduce redundancy?", "normalization"),
            ("Which normal form removes repeating groups?", "1NF"),
            ("Which normal form eliminates partial dependency?", "2NF"),
            ("What is a benefit of normalization?", "reduces redundancy"),
        ],
        20: [
            ("What does ACID stand for?", "Atomicity, Consistency, Isolation, Durability"),
            ("Which command saves a transaction?", "COMMIT"),
            ("Which command undoes a transaction?", "ROLLBACK"),
            ("What ensures multiple operations behave as one unit?", "transaction"),
            ("Which property ensures changes persist after commit?", "durability"),
        ],

        # Computer Science (lessons 21..25)
        21: [
            ("What is the Big-O of linear search?", "O(n)"),
            ("What is the Big-O of binary search?", "O(log n)"),
            ("Which sorting algorithm is O(n log n) average?", "merge sort"),
            ("What does algorithm correctness mean?", "produces correct output"),
            ("What is an example of a greedy algorithm?", "Dijkstra (with non-negative weights)"),
        ],
        22: [
            ("Which data structure uses LIFO order?", "stack"),
            ("Which data structure uses FIFO order?", "queue"),
            ("How do you add to the end of a Python list?", "append()"),
            ("What structure maps keys to values?", "dictionary"),
            ("Which DS is ideal for undo operations?", "stack"),
        ],
        23: [
            ("What does O(n^2) indicate about an algorithm?", "quadratic time"),
            ("What is constant time complexity?", "O(1)"),
            ("Which is better: O(n) or O(n^2)?", "O(n)"),
            ("What does 'n' typically represent?", "input size"),
            ("What measures memory usage?", "space complexity"),
        ],
        24: [
            ("Which paradigm uses classes and objects?", "OOP"),
            ("Which paradigm emphasizes pure functions?", "functional"),
            ("Which uses step-by-step instructions?", "procedural"),
            ("What is encapsulation in OOP?", "hiding internal state"),
            ("What is inheritance used for?", "code reuse"),
        ],
        25: [
            ("What component executes instructions in a computer?", "CPU"),
            ("What stores data temporarily for running programs?", "RAM"),
            ("What is a small fast memory between CPU and RAM?", "cache"),
            ("What does ALU stand for?", "Arithmetic Logic Unit"),
            ("Which component stores long-term data?", "disk/storage"),
        ],
    }

    # Insert questions from the mapping
    for quiz_id, qa_list in questions.items():
        for q, a in qa_list:
            cursor.execute(
                "INSERT OR IGNORE INTO quiz_questions (quiz_id, question, correct_answer) VALUES (?, ?, ?)",
                (quiz_id, q, a),
            )

    conn.commit()
    conn.close()

    print("✅ Sample data inserted: 5 courses, lessons, quizzes, and questions")


if __name__ == "__main__":
    insert_sample_data()
