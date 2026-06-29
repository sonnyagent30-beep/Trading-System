import numpy as np
import pandas as pd

def full_matrix():
    df = pd.DataFrame(np.random.rand(10, 10))
    print(df)
    return df

if __name__ == "__main__":
    full_matrix()
