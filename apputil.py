import seaborn as sns

# update/add code below ...
def fibonacci(n):
    """
    Return the n-th Fibonacci number using recursion.
    n: index (0-based) in the Fibonacci sequence.
    Example: fib(9) -> 34
    """
    # Base cases
    if n == 0:
        return 0
    elif n == 1:
        return 1
    
    # Recursive case
    return fibonacci(n - 1) + fibonacci(n - 2)

# Test
print(fibonacci(9))     



def to_binary(n):
    """
    Convert a non-negative integer n to its binary representation as a string.
    Example:
        to_binary(2)  -> '10'
        to_binary(12) -> '1100'
    """
    # Handle 0 and 1 directly (base cases)
    if n < 2:
        return str(n)
    
    # Recursive case: divide by 2, recurse on the quotient, then append remainder
    return to_binary(n // 2) + str(n % 2)

# Tests
print(to_binary(2))    # Output: '10'
print(to_binary(12))   # Output: '1100'
print(to_binary(0))    # Output: '0'
print(to_binary(1))    # Output: '1'

# Compare to Python's built-in bin()
print(bin(12)[2:])     # Output: '1100'






# Assuming df_bellevue is already loaded globally
# If it's inside a Jupyter cell, this will still work.

#  Task 1: List of column names sorted by missing values
def task_1():
    global df_bellevue
    
    # Fix the 'gender' column issue if any (example: inconsistent case or spelling)
    if 'gender' in df_bellevue.columns:
        print("Standardizing 'gender' column to handle inconsistencies...")
        df_bellevue['gender'] = df_bellevue['gender'].str.strip().str.lower()
        # Common mapping if needed:
        df_bellevue['gender'] = df_bellevue['gender'].replace({
            'm': 'male', 'f': 'female'
        })
    
    # Count missing values per column
    missing_counts = df_bellevue.isna().sum()
    # Sort by ascending missing values
    sorted_columns = missing_counts.sort_values().index.tolist()
    return sorted_columns


#  Task 2: DataFrame with year and total admissions per year
def task_2():
    global df_bellevue
    
    # Check if there's a 'year' column
    if 'year' not in df_bellevue.columns:
        print("No 'year' column found — check dataset column names.")
        return None
    
    df_counts = (
        df_bellevue
        .groupby('year')
        .size()
        .reset_index(name='total_admissions')
    )
    return df_counts


#  Task 3: Series with gender as index, average age as values
def task_3():
    global df_bellevue
    
    if 'gender' not in df_bellevue.columns or 'age' not in df_bellevue.columns:
        print("Missing 'gender' or 'age' column — cannot compute average age.")
        return None
    
    avg_age_by_gender = (
        df_bellevue
        .groupby('gender')['age']
        .mean()
    )
    return avg_age_by_gender


#  Task 4: List of 5 most common professions (in order)
def task_4():
    global df_bellevue
     
    if 'profession' not in df_bellevue.columns:
        print("Missing 'profession' column.")
        return None
    
    top_5_professions = (
        df_bellevue['profession']
        .value_counts()
        .head(5)
        .index
        .tolist()
    )
    return top_5_professions


# -------------------------------
# Example of calling the functions:
# -------------------------------
print(task_1())
print(task_2())
print(task_3())
print(task_4())



  



