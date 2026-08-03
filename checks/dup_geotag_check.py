from quad.state import get_state
from quad.survey import harvasine

state = get_state()

tags = state.geotags

def rem_duplicate_tags():
    left  = 0 
    right = 1

    while left != right:
        if harvasine(
            state.geotags[left][0],
            state.geotags[left][1], 
            state.geotags[right][0],
            state.geotags[right][1]
            ) <= 1.0:
            del state.geotags[right]
            right -= 1

        if right == len(state.geotags) - 1:
            left += 1
            right = left + 1

        right += 1
        

        
