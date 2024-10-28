from typing import Literal


pdxl_preset = ['score_9', 'score_8_up', 'score_7_up', 'score_6_up', 'score_5_up', 'score_4_up']
tier_preset = ['S-Tier', 'A-Tier', 'B-Tier', 'C-Tier', 'D-Tier', 'F-Tier']
numeric_tier_preset = ['Tier 1', 'Tier 2', 'Tier 3', 'Tier 4', 'Tier 5', 'Tier 6']
performance_tier_preset = ['Outstanding', 'Excellent', 'Good', 'Average', 'Below Average', 'Poor']
star_tier_preset = ['★★★★★', '★★★★☆', '★★★☆☆', '★★☆☆☆', '★☆☆☆☆', '☆☆☆☆☆']
booru_tier_preset = ['masterpiece', 'high quality', 'good quality', 'average', 'low quality', 'poor quality']

def get_preset(name: Literal['pdxl', 'booru-tier', 'alphabetical-tier', 'numeric-tier', 'performance-tier', 'star-tier']):
    if name == 'pdxl':
        return 'pdxl', pdxl_preset
    elif name == 'booru-tier':
        return 'booru-tier', booru_tier_preset
    elif name == 'alphabetical-tier':
        return 'alphabetical-tier', tier_preset
    elif name == 'numeric-tier':
        return 'numeric-tier', numeric_tier_preset
    elif name == 'performance-tier':
        return 'performance-tier', performance_tier_preset
    elif name == 'star-tier':
        return 'star-tier', star_tier_preset
    else:
        print(f"Unknown preset: '{name}'. Falling back to PDXL...")
        return 'pdxl', pdxl_preset
    
def get_preset_list():
    return ['pdxl', 'booru-tier', 'alphabetical-tier', 'numeric-tier', 'performance-tier', 'star-tier']