
# Number words
units = [
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen",
]
tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
scales = ["hundred", "thousand", "million", "billion", "trillion"]

number_words = units + tens + scales

# Number scale
num_scale = {"hundred": 10**2,
             "thousand": 10**3,
             "million": 10**6,
             "billion": 10**9,
             "trillion": 10**12}