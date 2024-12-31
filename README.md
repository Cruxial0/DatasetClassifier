# DatasetClassifier
A new spin on manual dataset curation

## Introduction
DatasetClassifier is a customizable tool aimed at speeding up the workflow of manual dataset curation. The idea behind this application is to speed up the process of reviewing and captioning images.

### Motivations
I'll admit, I might be a bit crazy. I like to create datasets of a broad concept, so what I often do is I boot up [Grabber](https://github.com/Bionus/imgbrd-grabber), type in some tags, and suddenly I am left with a dataset of tens of thousands of images. Obviously, not all these images are worth keeping, so manual review is needed. The first time around, I painstakingly drag/dropped images in Windows File Explorer into different folders to sort them. Never again, I said to myself, then a few weeks later I was back at it again, with an even larger dataset...

I think you see where I'm going with this. Dragging/Dropping images in Windows File Explorer is not very fun.

Surprisingly, there were no good options for manual dataset review that met my criteria, so that's where the idea came from.

### Structure
DatasetClassifier has two main parts:
1. **The Scoring Part** - This is where you sift through images. You can assign a score to each image, or discard it completely. You can also add categories to images, which will be explained more in detail later.
2. **The Tagging Part** - This is a reimagined tagging process based around my personal needs. You can define your own checklist which you will have to step through for each image.

#### Scoring
The scoring process is relatively straight-forward. You see an image, you determine how good that image is for your dataset, and you apply the corresponding score. In my own testing, I am able to get through about 2-3k images per hour using this approach (this rate is without any categorization).

Categories are a way to provide additional information to your images, which can later be used to seperate them into their own directories based on category combinations. Here's an example of how you might use them:

Let's say you define two categories, based on how much manual work they need: `needs_editing` and `needs_cropping`. For each image, you can apply the relevant categories. Later when you export these images, you can define rules that export images with the `needs_editing` category into it's own subfolder, and `needs_cropping` into another subfolder. You can also define a rule to export images with both categories into a third subfolder.

#### Tagging
The tagging process has a little bit of a learning curve to understand correctly. It works using `Tags` and `TagGroups`. A `TagGroup` is essentially a collection of tags, as the name suggests. It allows you to define conditions that must be met before moving on to tagging the next image. Here's an example of how you may configure your `TagGroups` (using booru tags as an example):
```
# Subjects:
- 1girl
- 2girls
- 3girls

Background:
- simple background
- classroom
- scenery

Composition:
- portrait
- group photo
- overview
```

In this example, you would first select one or more tags from the "# Subjects" group, then move on to the "Background" group and select the relevant tag for that group. This process repeats for every image.

Each group is customizable, so if we wanted the "Composition" group to be optional, we could do that. If we want to enforce **at least** two tags for the "Background" group, we can do that too.

## Customization
DatasetClassifier is built around the principle of customization. Most things can be customized, including: App Behaviour, Theme Colors, Keybinds, etc.

Some of the more advanced customizations will be explained here.

### Tag Groups
TagGroups are created on a per-project basis. Each group can contain practically unlimited tags.

Here is an explanation of each property of a TagGroup:
- **Required:** Whether or not the TagGroup has to be completed in order to proceed
- **Allow Multiple:** Whether or not the TagGroup allows multiple tags to be selected
- **Minimum Tags:** Minimum amount of tags required to proceed
- **Prevent Auto Scroll:** Whether or not to automatically scroll to the next TagGroup when the current TagGroup's condition is met

### Rule-based export
With rule based export, you can define your own rules.

Here is an example of how the export window might look:
![image](https://github.com/user-attachments/assets/26bdcf0d-728b-4866-93a0-10c6be9a92ce)

Exports work with priorities. It starts with the highest priority, then works it's way down the list. All images that don't meet a rule will be exported to the base directory.

#### Rule Ordering
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

## Plans
- [ ] **Conditional TagGroups:** TagGroups that can only be accessed if a certain condition is met, for example if `X` tag has been added or `Y` TagGroup is finished
- [ ] **Conditional Tags:** Tags that will automatically be added on export. Conditions will be customizable.
- [ ] **Export Window Rework:** The export window is not in a good state (but usable for now). It needs a full rewrite.
- [ ] **Project Export/Import:** A feature to import/export a project with all it's TagGroups, images and tag data.

## Installation
### Windows
1. Install Python (version 3.8 or greater)
2. Clone the repository with `git clone https://github.com/Cruxial0/DatasetClassifier.git`
3. Run `run-win.bat`
### Mac
1. Install Python (version 3.8 or greater)
2. Clone the repository with `git clone https://github.com/Cruxial0/DatasetClassifier.git`
3. Open a terminal in the cloned folder
4. Run command: `sh run-mac.sh`
### Linux
Not tested

## Contributing
Contributions are welcome and encouraged!
