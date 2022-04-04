# NEA

# Version 6: 
  # [Fixed death animatino position changing] : 
  # [Fixed an issue with wall collision due to inconsistent player size] : changed the dimensions of player falling and jumping animations to match idling and other states so it remains constant and prevents tile collision from messing up. Initially due to change in sizes even though collision may not occur in idle state, if player was falling/jumping the width was smaller which meant that after landing/collision and reverting back to idle/running state it would trigger a collision because those states' widts were bigger

  # [Fixed death animation position changing] : during enemy AI, the enemy goes into an idle state once they have walked their assigned distance in a direction whereafter they change directions to repeat the process. However, when the check was made to see if they should switch, the direction would be changed and then they would go into an idle state in the direction of motion prior to change; but the self.direction would be flipped which led to the image of death animation changing when they died in an idle state due to change in direction. Fixed this by changing the direction of motion after the idle state was finished
