# DatasetClassifier
A simple tool to help you speed up your workflow when manually scoring and categorizing images.

# DatasetClassifier

## Overview
DatasetClassifier is an efficient image browser with advanced classification features. It utilizes PonyDiffusion's rating convention to score images from `score_9` to `score_4_up`.

![DatasetClassifier Interface](https://github.com/user-attachments/assets/20d55a39-b5c4-438c-b7a2-1f9ddef0e3f6)

## Key Features
1. **Simple Interface**: Select input and output folders at the top of the application.
2. **Image Browser**: Central panel displays the current image for classification.
3. **Categorization**: Assign multiple categories to each image for detailed organization.
4. **Flexible Output**: Images are saved in both the main scoring folder and respective category folders.

## File Structure Example
```
📁 output
  ├─ score_8_up
  │   ├─ classroom
  │   │   └─ image.png
  │   ├─ white background
  │   └─ image.png
  └─ score_9
```

## Keyboard-Centric Design
DatasetClassifier prioritizes efficiency with a keyboard-driven interface. All functions have customizable keybinds, configured through the `config.yaml` file.

### Default Keybinds
```yaml
# Scoring
score_9: '1'
score_8_up: '2'
score_7_up: '3'
score_6_up: '4'
score_5_up: '5'
score_4_up: '6'
discard: 'ESC'

# Categories
custom_1: Alt+1
custom_2: Alt+2
custom_3: Alt+3
custom_4: Alt+4
custom_5: Alt+5
custom_6: Alt+6
custom_7: Alt+7
custom_8: Alt+8
custom_9: Alt+9
custom_10: Alt+0

# Image Navigation
image_next: Right
image_previous: Left
```

Customize your workflow by modifying these keybinds in the configuration file to suit your preferences.

## Installation
### Windows
1. Install Python (version 3.8 or greater)
2. Clone the repository with `git clone https://github.com/Cruxial0/DatasetClassifier.git`
3. Run `run.bat`
