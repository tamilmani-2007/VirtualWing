from quad.state import get_state
from quad.survey import harvasine

state = get_state()

tags = state.geotags

def rem_duplicate_tags():
    left  = 0 

    while left < len(state.geotags) - 1:
        right = left + 1

        while right < len(state.geotags):
        
            if harvasine(
                state.geotags[left][0],
                state.geotags[left][1], 
                state.geotags[right][0],
                state.geotags[right][1]
                ) <= 1.0:
                    
                    del state.geotags[right]
            else:
                 right += 1
             

        left += 1

        
