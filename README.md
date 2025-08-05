# Blender Parameterization Helper

## Overview

The purpose of this repository is to host a tool that will take blender code for parameterized modelling of chainmail weaves and return modified code that will model the weave in addition to adding a custom UI allowing you to modify the parameters from a UI and offer a keyboard control method.

Below is an example of the custom UI added to blender.

![Custom Blender UI Example](assets/example.png)


## Expected Code Format

As this program takes code as input, it expects the code to follow a certain layout to run smoothly. 

The script looks for headings to separate the two sections it needs to read, `Parameters` and `Model Code`. Below are explainations of how to format section headings, and explainations of the two sections.

### Section Headings

Section headings should take the form of 3 comments on a group of three lines of the following format:

* The first line should be just hashes (`#`) the from the start to the length of the second line.

* The second line is comprised of three parts:
    * The first part is three hashes followed by a space (`### `).
    * The second part is the section name as a capitalized spaced string (`This Is My Section`).
    * The third part is a space followed by three hashes (` ###`).

* The third line should be just hashes (`#`) the from the start to the length of the second line.

An example section heading is:

    ####################
    ### Section Name ###
    ####################

### Parameters


### Model Code


## Goals

* Write a standalone executable for windows
* Make a 1 page app hosted via GH pages
* Add support for variables composed of other variables
