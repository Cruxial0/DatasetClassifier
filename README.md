# DatasetClassifier
A simple tool to help you speed up your workflow when manually scoring and categorizing images.

## Explanation
DatasetClassifier is a simple image browser, with a few extra features. It uses PonyDiffusion's rating convention to score images from `score_9` to `score_6_up`.

![image](https://github.com/user-attachments/assets/20d55a39-b5c4-438c-b7a2-1f9ddef0e3f6)


This image shows how the main application works.
At the top, you select your input folder (where your images are) and your output folder (where your images end up)
In the middle, you have your image browser and categories. The image browser just shows you the image you're classifying, while categories allow you to further group your images into smaller subsets. By default, an image with a category will be copied to **both** the main scoring folder, aswell as the category folder(s).

Here is a visual representation using the example image above
```
📁 output
  ├─ score_8_up
  │   ├─ classroom
  │   │   └─ image.png
  │   ├─ white background
  │   └─ image.png
  └─ score_9
 ```

DatasetClassifier works with a keyboard-only philosophy. Nearly everything has keybinds, all of which are configurable through the `config.yaml` file.
Here is a list of default keybinds:
```yaml
# scoring
score_9: '1'
score_8_up: '2'
score_7_up: '3'
score_6_up: '4'
score_5_up: '5'
score_4_up: '6'
discard: 'ESC'

# categories
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

# image browser
image_next: Right
image_previous: Left
```

## Installation
### Windows
1. Install Python (version 3.8 or greater)
2. Clone the repository with `git clone https://github.com/Cruxial0/DatasetClassifier.git`
3. Run `run.bat`
