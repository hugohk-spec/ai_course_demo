"""
================================================================================
BASIC PYTHON CONCEPTS
================================================================================
Topics to cover:
• Print statements
• Variables and data types
• Basic operations
• Lists
• If conditions
• Loops
================================================================================
"""

# ============================================================================
# 1. PRINT STATEMENTS
# ============================================================================
print("Hello World!")  # Displays: Hello World!
print(123)            # Displays: 123
# Note: Print is like talking to the computer. Whatever you put inside print() 
# will show up on the screen.

# ============================================================================
# 2. VARIABLES & DATA TYPES
# ============================================================================
name = "John"         # String
age = 15             # Integer
height = 1.75        # Float
is_student = True    # Boolean

# Note: Variables are like containers that store different types of information. 
# Think of them as labeled boxes where you can put numbers, text, or yes/no values.

print(f"Name: {name}, Age: {age}, Height: {height}, Is Student: {is_student}")

# ============================================================================
# 3. BASIC OPERATIONS
# ============================================================================
# Numbers
x = 10 + 5           # Addition
y = 20 - 8           # Subtraction
z = 4 * 3            # Multiplication
w = 15 / 3           # Division

print(f"x = {x}, y = {y}, z = {z}, w = {w}")

# Strings
first = "Hello"
last = "World"
full = first + " " + last  # String concatenation
print(full)

# Note: You can do math with numbers and combine words (strings) together. 
# The '+' symbol works differently for numbers (adds them) and strings (joins them).

# ============================================================================
# 4. LISTS
# ============================================================================
fruits = ["apple", "banana", "orange"]
print(fruits[0])     # Gets first item: apple
fruits.append("grape")  # Adds to list
print(fruits)

# Note: Lists are like shopping lists - they can hold multiple items in order. 
# Remember that computers start counting from 0, so the first item is at position 0.

# ============================================================================
# 5. IF CONDITIONS
# ============================================================================
age = 15
if age < 13:
    print("Primary")
elif age < 16:
    print("Secondary")
else:
    print("Senior")

# Note: If-conditions are like making decisions. The computer checks if something 
# is true, and then does different things based on the answer.

# ============================================================================
# 6. LOOPS
# ============================================================================
# For loop with range
for i in range(3):
    print(i)         # Prints: 0, 1, 2

# For loop with list
fruits = ["apple", "banana", "orange"]
for fruit in fruits:
    print(fruit)

# Note: Loops help you do the same thing many times. It's like telling the computer 
# to repeat something instead of writing it multiple times.
