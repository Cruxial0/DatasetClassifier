# DatasetClassifier
A simple tool to help you speed up your workflow when manually scoring and categorizing images.

## Overview
DatasetClassifier is an efficient and customizable image browser combined with categorization and scoring features. The purpose of DatasetClassifier is to speed up the manual workflow of curating larger datasets. I created it as no real alternatives existed at the time, with the best alternative being manually dragging/dropping images into folders in windows file explorer.

As an example workflow, I usually use this tool to quickly curate and discard unwanted images from large datasets downloaded from booru. I like to make models of broad subjects, so the datasets usually end up being around 20-30k images. Using this tool, I can get through about 3-4 thousand images an hour, making it much more efficient (not to mention less straining) than windows file explorer.

![DatasetClassifier Interface](https://github.com/user-attachments/assets/20d55a39-b5c4-438c-b7a2-1f9ddef0e3f6)

## Key Features
1. **Simple Interface**: Select input and output folders at the top of the application.
2. **Image Browser**: Central panel displays the current image for classification.
3. **Categorization**: Assign multiple categories to each image for detailed organization.
4. **Flexible Output**: Images are saved in both the main scoring folder and respective category folders.
5. **Rule-based Export**: You can define your own rules and customize the export pattern.
6. **Customization**: Many parts of the interface can be customized to better suit your needs.

## Rule-based export
With rule based export, you can define your own rules.

Here is an example of how the export window might look:
![image](https://github.com/user-attachments/assets/26bdcf0d-728b-4866-93a0-10c6be9a92ce)

Exports work with priorities. It starts with the highest priority, then works it's way down the list. All images that don't meet a rule will be exported to the base directory.

### Rule Ordering
Say you have these categories: `needs editing, needs cropping, complete`

You may want to export images that need a large amount of manual edits to it's own folder, while still storing other files to their respective output paths. This can be done by selecting multiple categories.
However, in this case, the ordering of your rules is important. Here is a general rule of thumb:
```yaml
- Category Combinations
- Single Categories
- Fallback Rule
```
In short, more specific rules need to have a higher priority. If you have a rule that require three categories, it should almost always be over a rule that require two or less.

Here is an example of how you would configure an export for the example above:
```yaml
3.    ['needs editing', 'needs cropping']    './heavy_edits'
2.    ['needs editing']                      './needs_edits'
1.    ['needs cropping']                     './needs_cropping'
0.    []                                     '.'
```

In this example, all images with both the `needs editing` and `needs cropping` categories will be exported to `./heavy_edits`, while images that only contain either `needs editing` or `needs cropping` will be exported to their respective folders. Images with the `completed` category, or without categories will be exported to the root of the export directory.

### Options
**Seperate by Score:** Seperates all images by score, then by category. Images that would be saved to `.` will instead be saved to `./score_9`, `./score_8_up` etc.

## Keyboard-Centric Design
DatasetClassifier prioritizes efficiency with a keyboard-driven interface. All functions have customizable keybinds, configured through the provided settings interface, or by manually editing the `config.yaml` file.
The application works with modifier layers. By default, all keybinds are on the middle row of the keyboard (Based on the English QWERTY layout). Using the ALT modifier toggles categories, while CTRL removes categories. Holding ALT or CTRL will highlight which buttons they affect. I encourage you to play around with these, as they will massively speed up your workflow.

### Default Keybinds
```yaml
# Scoring
key_0: A # score_9
key_1: S # score_8_up
key_2: D # score_7_up
key_3: F # score_6_up
key_4: G # score_5_up
key_5: H # score_4_up
key_6: J
key_7: K
key_8: L
key_9: ;
discard: BACKSPACE

# Navigation
image_next: Right
image_previous: Left
```

## Customization
Customization is always a core principle of mine. I have added support for customizing things such as keybinds, color themes and scoring presets.

### Scoring Presets
Scoring Presets are the visual sugar to your scoring. By default it uses the PonyDiffusion convention, which goes as follows:
```
score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up
```
Understandably, this convention is critiziced by some, which is why DatasetClassifier lets you choose between 6 different scoring presets:
```yaml
pdxl_preset = ['score_9', 'score_8_up', 'score_7_up', 'score_6_up', 'score_5_up', 'score_4_up']
tier_preset = ['S-Tier', 'A-Tier', 'B-Tier', 'C-Tier', 'D-Tier', 'F-Tier']
numeric_tier_preset = ['Tier 1', 'Tier 2', 'Tier 3', 'Tier 4', 'Tier 5', 'Tier 6']
performance_tier_preset = ['Outstanding', 'Excellent', 'Good', 'Average', 'Below Average', 'Poor']
star_tier_preset = ['★★★★★', '★★★★☆', '★★★☆☆', '★★☆☆☆', '★☆☆☆☆', '☆☆☆☆☆']
booru_tier_preset = ['masterpiece', 'high quality', 'good quality', 'average', 'low quality', 'poor quality']
```

## Installation
### Windows
1. Install Python (version 3.8 or greater)
2. Clone the repository with `git clone https://github.com/Cruxial0/DatasetClassifier.git`
3. Run `run.bat`
### Mac
1. Install Python (version 3.8 or greater)
2. Clone the repository with `git clone https://github.com/Cruxial0/DatasetClassifier.git`
3. Open a terminal in the cloned folder
4. Run command: `sh run.sh`
### Linux
Not tested

## Contributing
Contributions are welcome and encouraged!
