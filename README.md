# DatasetClassifier
A simple tool to help you speed up your workflow when manually scoring and categorizing images.

## Overview
DatasetClassifier is an efficient image browser with advanced classification features. It utilizes PonyDiffusion's rating convention to score images from `score_9` to `score_4_up`.

![DatasetClassifier Interface](https://github.com/user-attachments/assets/20d55a39-b5c4-438c-b7a2-1f9ddef0e3f6)

## Key Features
1. **Simple Interface**: Select input and output folders at the top of the application.
2. **Image Browser**: Central panel displays the current image for classification.
3. **Categorization**: Assign multiple categories to each image for detailed organization.
4. **Flexible Output**: Images are saved in both the main scoring folder and respective category folders.
5. **Rule-based Export**: You can define your own rules and customize the export pattern

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
DatasetClassifier prioritizes efficiency with a keyboard-driven interface. All functions have customizable keybinds, configured through the `config.yaml` file.
The application works with modifier layers. By default, all keybinds are on the middle row of the keyboard (Based on the English QWERTY layout). Using the ALT modifier toggles categories, while CTRL removes categories. Holding ALT or CTRL will highlight which buttons they affect.

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

Customize your workflow by modifying these keybinds in the configuration file to suit your preferences.

## Installation
### Windows
1. Install Python (version 3.8 or greater)
2. Clone the repository with `git clone https://github.com/Cruxial0/DatasetClassifier.git`
3. Run `run.bat`
### Linux
Not tested

## Contributing
Contributions are welcome and encouraged!
