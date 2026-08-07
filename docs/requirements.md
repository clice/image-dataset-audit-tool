# Image Dataset Audit Tool — Requirements

## 1. Purpose

The Image Dataset Audit Tool is a Python command-line application designed to inspect the structure and basic quality characteristics of image classification datasets.

The application performs read-only analysis and must not modify the original dataset.

## 2. Version Scope

Version 1.0 focuses exclusively on dataset auditing.

The application is responsible for:

1. discovering dataset structure;
2. inspecting image files;
3. calculating descriptive dataset statistics;
4. identifying common structural or file-integrity issues;
5. generating structured and human-readable reports.

Dataset transformation, correction, reorganization, labeling, preprocessing, and machine-learning operations are outside the scope of Version 1.0.

## 3. Dataset Assumptions

Version 1.0 assumes a directory-based classification dataset.

Each first-level directory below the dataset root represents one class.

Example:

```text
dataset/
├── class_a/
│   ├── image_001.jpg
│   └── image_002.png
├── class_b/
│   └── image_003.jpg
└── class_c/
    └── image_004.webp
```

Files located recursively below a class directory inherit the first-level directory as their class.

Class and file processing should use deterministic ordering whenever possible.

## 4. Initial Image Extensions

The initial implementation should recognize the following image extensions as audit candidates:

* `.jpg`
* `.jpeg`
* `.png`
* `.bmp`
* `.tif`
* `.tiff`
* `.webp`

Extension matching should be case-insensitive.

The file extension and the image format detected from the file contents should be treated as separate information.

---

# 5. Functional Requirements

## FR-01 — Dataset input

The system shall accept a path to a dataset directory.

## FR-02 — Dataset path validation

The system shall verify that the provided dataset path:

* exists;
* represents a directory;
* can be accessed by the application.

An invalid dataset path shall produce a clear error instead of an unhandled exception.

## FR-03 — Class discovery

The system shall identify first-level directories under the dataset root as dataset classes.

## FR-04 — Empty-class detection

The system shall identify classes that contain no supported image candidates.

## FR-05 — Image candidate discovery

The system shall discover supported image files contained under each detected class directory.

File-extension matching shall be case-insensitive.

## FR-06 — Recursive class scanning

The system shall allow supported image files to be discovered recursively below each first-level class directory.

The first-level directory shall remain the image class regardless of deeper directory nesting.

## FR-07 — Deterministic ordering

The system shall process and report classes and file paths using deterministic ordering whenever practical.

## FR-08 — Image counting

The system shall calculate:

* the total number of discovered image candidates;
* the number of discovered image candidates per class.

## FR-09 — Unsupported-file accounting

The system should count files encountered within class directories that are not recognized as supported image candidates.

Unsupported files shall not stop the audit.

## FR-10 — Image extension collection

The system shall record the filename extension of each discovered image candidate.

## FR-11 — Image format detection

The system shall attempt to identify the actual image format from the image contents.

## FR-12 — Image dimension inspection

For each valid image, the system shall collect:

* width;
* height.

## FR-13 — Image integrity validation

The system shall verify whether each discovered image candidate can be successfully interpreted as an image.

## FR-14 — Corrupted-image registration

When an image cannot be successfully validated, the system shall record:

* relative file path;
* associated class;
* failure status;
* available error information.

## FR-15 — Fault-tolerant processing

A corrupted, unreadable, or otherwise invalid individual image shall not terminate the complete dataset audit whenever processing can safely continue.

## FR-16 — Relative report paths

File paths stored in generated reports should be relative to the dataset root whenever possible.

## FR-17 — Class distribution

The system shall calculate for each class:

* absolute image count;
* percentage of discovered image candidates.

## FR-18 — Class imbalance indicator

The system shall calculate a descriptive imbalance ratio based on the largest and smallest non-empty classes.

The ratio shall be treated as descriptive information.

The application shall not present a universal threshold as proof that a dataset is balanced or imbalanced.

## FR-19 — Dimension summary

The system shall calculate basic dimension statistics for valid images, including:

* minimum width;
* maximum width;
* minimum height;
* maximum height.

Additional descriptive statistics may be introduced when they provide clear analytical value.

## FR-20 — Terminal summary

The system shall display a concise audit summary after execution.

The summary should include at least:

* number of classes;
* discovered image count;
* valid image count;
* corrupted image count;
* basic class-distribution information;
* generated report locations.

## FR-21 — CSV report

The system shall generate a detailed CSV report containing one record for each inspected image candidate.

The initial schema shall contain fields equivalent to:

```text
path
class
extension
format
width
height
status
error
```

## FR-22 — JSON report

The system shall generate a structured JSON document containing aggregated audit statistics.

The JSON report should include information equivalent to:

* dataset identifier;
* number of classes;
* total discovered images;
* valid image count;
* corrupted image count;
* class counts;
* class percentages;
* empty classes;
* image-format counts;
* dimension statistics;
* imbalance ratio;
* unsupported-file count.

## FR-23 — PDF audit report

The system shall generate a human-readable PDF report summarizing the audit.

The PDF should include:

* dataset overview;
* class-distribution information;
* basic charts;
* image-format information;
* image-dimension information;
* corrupted-image summary;
* data-quality warnings when applicable.

## FR-24 — Configurable output location

The application shall allow generated reports to be written to an output directory.

A default output directory may be used when no explicit location is provided.

## FR-25 — Read-only dataset operation

The system shall not:

* modify;
* rename;
* move;
* delete;
* resize;
* convert;
* overwrite

any source dataset file.

## FR-26 — Local Python execution

The system shall support execution in a local Python environment.

## FR-27 — Docker execution

The project shall provide a lightweight Docker configuration for reproducible execution.

Dataset and report directories shall remain outside the container and should be supplied through mounted directories.

## FR-28 — Alternative Python environments

The core Python implementation shall avoid unnecessary environment-specific assumptions so that it can also be executed in compatible notebook environments such as Google Colab.

---

# 6. Non-Functional Requirements

## NFR-01 — Programming language

The application shall be implemented in Python.

## NFR-02 — Simplicity

The project shall avoid architectural components and infrastructure that do not provide a clear benefit to the defined problem.

## NFR-03 — Portability

The core application should avoid unnecessary operating-system-specific behavior.

## NFR-04 — Reproducibility

Runtime dependencies and supported Python versions shall be explicitly declared.

## NFR-05 — Dataset safety

The source dataset shall be treated as read-only.

## NFR-06 — Reliability

Individual invalid files shall be handled without causing the complete audit to terminate whenever recovery is possible.

## NFR-07 — Deterministic results

Given an unchanged dataset and equivalent software environment, repeated executions should produce equivalent audit statistics.

## NFR-08 — Maintainability

Dataset discovery, image inspection, dataset analysis, and report generation should remain sufficiently separated to allow independent testing and evolution without introducing unnecessary architectural layers.

## NFR-09 — Testability

Core behavior shall be designed so that dataset discovery, validation, statistics, and reporting can be covered by automated tests.

## NFR-10 — Documentation

The project shall document:

* project purpose;
* supported dataset structure;
* installation;
* local execution;
* Docker execution;
* generated outputs;
* known limitations.

## NFR-11 — Dependency control

External dependencies shall only be introduced when they provide a clear implementation or maintainability benefit.

## NFR-12 — Resource proportionality

The application should process datasets incrementally where practical and avoid unnecessarily loading complete image collections into memory.

---

# 7. Version 1.0 Outputs

The default report set is:

```text
reports/
├── images.csv
├── summary.json
└── audit_report.pdf
```

The report directory is generated separately from the source dataset.

---

# 8. Version 1.0 Exclusions

Version 1.0 shall not include:

* model training;
* model inference;
* image classification;
* object detection;
* image preprocessing pipelines;
* data augmentation;
* automatic class balancing;
* automatic dataset correction;
* automatic file renaming;
* automatic class reorganization;
* automatic train/validation/test splitting;
* database integration;
* web or graphical interfaces;
* REST APIs;
* distributed processing;
* GPU-specific processing;
* DICOM-specific analysis;
* duplicate-image detection;
* visual-similarity analysis;
* automatic Kaggle dataset acquisition;
* patient-level leakage analysis;
* medical metadata validation.

---

# 9. Milestones

## M0 — Scope & Requirements

Define and document Version 1.0.

## M1 — Dataset Discovery

Implement input validation, class discovery, file discovery, and initial counts.

## M2 — Image Inspection

Implement image validation, format detection, dimension extraction, and corrupted-file handling.

## M3 — Dataset Analysis

Implement class distribution, empty-class detection, dimension statistics, and imbalance analysis.

## M4 — Reporting

Implement terminal, CSV, JSON, PDF, and visualization outputs.

## M5 — Packaging & Quality

Complete tests, error handling, Docker support, documentation, Colab demonstration, and final review.

---

# 10. Version 1.0 Completion Criteria

Version 1.0 is complete when the application can:

1. accept and validate a directory-based image dataset;
2. identify classes;
3. discover supported image candidates;
4. count images globally and by class;
5. identify valid and corrupted images;
6. collect image formats and dimensions;
7. calculate class distribution;
8. calculate basic dimension statistics;
9. calculate a descriptive class imbalance ratio;
10. generate CSV, JSON, and PDF outputs;
11. display a terminal summary;
12. run locally;
13. run through the documented Docker workflow;
14. pass the main automated tests;
15. provide complete installation and usage documentation.

The source dataset must remain unchanged throughout the complete audit process.
