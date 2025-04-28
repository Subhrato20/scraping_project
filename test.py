import re
import csv
import io
from urllib.parse import unquote # To decode URL-encoded parts

# The input data as a multi-line string
data = """
PCH Innovations becomes Gentle Systems. [Learn more.](https://www.gentle.systems/page/pch)

# Curiosity, imagination, invention.

# Creative Engineering.

# Curiosity, imagination, invention. Creative Engineering.

## Highlight

[**Frei Otto**](https://www.gentle.systems/page/otto) [![](https://www.gentle.systems/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2F1c4tf0ju3bmy%2F4EoqDGngEDl2cwf3rwAFrw%2F1a29192de683b5bc31a56ca9474709e2%2Ftumblr_lo8mgsQZgj1qe0nlvo1_1280.jpg&w=3840&q=80)\\
\\
Light weight architecture studies. A new method for exploring complex geometries, using soap film as a medium.](https://www.gentle.systems/page/otto)

[**Experiments**](https://www.gentle.systems/page/otto) [Surface tension explorations.](https://www.gentle.systems/page/otto)

[**Otto — Choreography 1**](https://www.gentle.systems/page/otto) [![Image Asset](https://www.gentle.systems/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2F1c4tf0ju3bmy%2F5i7lL3Ds7wxOeqLGexdRhH%2F74a5c8c6e8ea48073318d8378ede5d4f%2FM02_PCH0758_01_SET_UP_368_WF_06.jpg&w=3840&q=80)\\
\\
Exploration of minimal surfaces.](https://www.gentle.systems/page/otto)

## 22.04.25

### Office Impression

![](https://www.gentle.systems/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2F1c4tf0ju3bmy%2F4UFXqfAZLibY6nyddvaWoU%2Ffed8aa5b00528c66ba80b767769071d6%2F250220_Gentle_Systems_082_CC.jpg&w=3840&q=80)

Studio artifact by Phillip Koll

## 08.04.25

### Prompt

#### 'Orbit around the dinosaur while doing a dolly shot and end with a view of both the chicken and the dino.'

### LLM x Robotics Experimentation

Here are the chicken and the dinosaur Aurélien and Matvey were talking about.

### Are we DoPs?

## 03.04.25

[**Frei Otto, Models**](https://www.youtube.com/watch?v=-IW7o25NmeA) [The inspiration for our robotic choreographies. Frei Otto used soap to create architectural models and replace complex calculations.](https://www.youtube.com/watch?v=-IW7o25NmeA)

[**Experimentation process**](https://www.gentle.systems/page/otto) [Experimentation and prototyping is a core part of our practice. Don't miss out the behind the scenes of Otto when visiting our project page.](https://www.gentle.systems/page/otto)

[**Discover Otto**](https://www.gentle.systems/page/otto) [![Haw-Lin Photography](https://www.gentle.systems/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2F1c4tf0ju3bmy%2F2MXDNPQi4nf2laFFP9eC1z%2F5317f9479deccb41a7730e91afae6893%2FOtto_03_gs_hawlin.jpg&w=3840&q=80)\\
\\
Inspired by Frei Otto's soap models, we created a series of robotic choreographies that pushed our approach to programming machines to a new realm. Explore the project.](https://www.gentle.systems/page/otto)

## 02.04.24

### Lunch conversation

Play

0:00

0:00

Aurelien and Matvey talk about dinosaurs, chicken, and LLMs.

## 01.04.25

### Coming soon...

Andrea presenting his CMF studies for our upcoming Future Toolbelt R&D.

### Implicit modelling

### Prototypes

![](https://www.gentle.systems/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2F1c4tf0ju3bmy%2F59BwRkaitflZZ7BPUI88Kq%2F25320c8d38c1787d55bb61365d8faa34%2FScreenshot_2025-03-30_at_19.58.36.png&w=3840&q=80)

Load more

12 entries
"""

# Regular Expressions
# Simple markdown link: [Text](URL)
link_re = re.compile(r"\[(.*?)\]\((.*?)\)")
# Image URLs (covering ![](url) and the _next/image format)
# It captures the core URL, potentially needing decoding for _next/image
img_re = re.compile(r"!\[.*?\]\((.*?)\)|!\[\]\((.*?)\)|(https://www.gentle.systems/_next/image\?url=([^&]+)&w=\d+&q=\d+)")
# Date format DD.MM.YY or DD.MM.YYYY
date_re = re.compile(r"^(\d{2}\.\d{2}\.\d{2,4})$")
# Headings (## or ###)
heading_re = re.compile(r"^(#{1,4})\s*(.*)")
# Taglines/Simple text lines
tagline_re = re.compile(r"^(Curiosity, imagination, invention|Creative Engineering|PCH Innovations becomes Gentle Systems)\.*")

results = []
current_date = None
current_heading = None
last_link_info = None # To potentially associate with an image/text that follows

lines = data.strip().split('\n')
i = 0
while i < len(lines):
    line = lines[i].strip()
    i += 1 # Increment early, adjust if lookahead happens

    if not line: # Skip empty lines
        continue

    row_data = {
        "Type": "Unknown",
        "Date": current_date,
        "Title/Heading": None, # Specific heading for this item
        "Image_URL": None,
        "Image_Caption/Description": None,
        "Link_URL": None,
        "Link_Text/Context": None,
        "Associated_Text": None,
        "Parent_Heading": current_heading # General heading for the section
    }

    # --- Check line type ---
    date_match = date_re.match(line)
    heading_match = heading_re.match(line)
    img_match = img_re.search(line)
    link_matches = list(link_re.finditer(line)) # Find all links on the line

    # --- Process based on type ---
    if date_match:
        current_date = date_match.group(1)
        current_heading = None # Reset heading when date changes
        # Usually don't add a row just for date, context for following lines
        continue # Don't add a row just for the date itself

    elif heading_match:
        level = len(heading_match.group(1))
        text = heading_match.group(2).strip()
        if level == 2: # Assuming ## is main section heading
           current_heading = text
        row_data["Type"] = f"Heading (H{level})"
        row_data["Title/Heading"] = text
        # Don't directly add if it's just a context setter like ## Date
        if not date_re.match(text):
            results.append(row_data)
        last_link_info = None # Reset link context on new heading
        continue # Processed this line

    elif img_match:
        row_data["Type"] = "Image"
        img_url_raw = img_match.group(1) or img_match.group(2) or img_match.group(3)

        # Handle the _next/image case specifically to get the decoded URL
        if "_next/image?url=" in img_url_raw:
            encoded_url_match = re.search(r"url=([^&]+)", img_url_raw)
            if encoded_url_match:
                row_data["Image_URL"] = unquote(encoded_url_match.group(1))
            else:
                 row_data["Image_URL"] = img_url_raw # Fallback
        else:
            row_data["Image_URL"] = img_url_raw

        # --- Lookahead for caption ---
        # Check next non-empty line(s) for potential caption
        caption_lines = []
        temp_i = i
        while temp_i < len(lines):
            next_line = lines[temp_i].strip()
            if not next_line: # Skip empty
                temp_i += 1
                continue
            # Stop if it looks like a new element (link, heading, date, another image)
            if link_re.search(next_line) or heading_re.match(next_line) or date_re.match(next_line) or img_re.search(next_line) or next_line.startswith("Load more") or next_line.endswith("entries"):
                break
            # Assume it's a caption/description line
            caption_lines.append(next_line)
            temp_i += 1

        if caption_lines:
            row_data["Image_Caption/Description"] = " ".join(caption_lines)
            i = temp_i # Advance main loop counter past the consumed caption lines

        # --- Associate with previous link? ---
        # If the image line ALSO contains a link or was preceded by one
        if link_matches:
            # Simple case: take the first link found on the image line itself
             row_data["Link_Text/Context"] = link_matches[0].group(1).strip()
             row_data["Link_URL"] = link_matches[0].group(2).strip()
             # If the link text IS the image tag, clear link text
             if row_data["Link_Text/Context"].startswith("!"):
                  row_data["Link_Text/Context"] = "Image Link" # Placeholder
        elif last_link_info:
             # If the *previous* line processed was *just* a link
             row_data["Link_Text/Context"] = last_link_info["text"]
             row_data["Link_URL"] = last_link_info["url"]

        results.append(row_data)
        last_link_info = None # Consumed
        continue

    elif link_matches:
        # Handle lines that are primarily links or contain links + text
        processed_link_on_line = False
        link_text_parts = []
        remaining_text = line
        last_end = 0

        for match in link_matches:
            start, end = match.span()
            link_text = match.group(1).strip()
            link_url = match.group(2).strip()

            # Capture text before the link
            pre_text = remaining_text[last_end:start].strip()
            if pre_text:
                 link_text_parts.append(pre_text)

            # Store link info - might be standalone or associated with text
            link_info = {"text": link_text, "url": link_url}

            # Attempt to combine link with surrounding text if simple
            row_data_link = row_data.copy() # Create copy for this specific link instance
            row_data_link["Type"] = "Link"
            row_data_link["Link_Text/Context"] = link_text
            row_data_link["Link_URL"] = link_url

            # Extract potential associated text on the same line after the link
            post_text_match = re.match(r"^\s*\[(.*?)\]", remaining_text[end:])
            if post_text_match:
                row_data_link["Associated_Text"] = post_text_match.group(1).strip()
                # Adjust end to consume this associated text if needed (simplistic)
                # end += len(post_text_match.group(0)) # Be careful with complex cases

            results.append(row_data_link)
            processed_link_on_line = True
            last_link_info = link_info # Store for potential association with NEXT line (e.g., image)

            last_end = end # Update position for next iteration

        # Capture any text remaining after the last link
        final_text = remaining_text[last_end:].strip()
        if final_text and not processed_link_on_line: # If the line was *only* text after processing links (or had no links)
            row_data["Type"] = "Text"
             # Check for taglines
            tag_match = tagline_re.match(final_text)
            if tag_match:
                 row_data["Type"] = "Tagline"

            if final_text == "Load more" or final_text.endswith(" entries"):
                 row_data["Type"] = "Meta"

            if final_text.startswith("Play") and "0:00" in final_text:
                 row_data["Type"] = "Media Reference"

            row_data["Associated_Text"] = final_text
            # Only add if it wasn't just consumed as part of a link structure
            # This logic might need refinement depending on how text/links mix
            if not processed_link_on_line or (processed_link_on_line and final_text):
                results.append(row_data)
            last_link_info = None # Reset if line ended with text


        elif not processed_link_on_line: # Line had no links, treat as simple text
             row_data["Type"] = "Text"
             # Check for taglines
             tag_match = tagline_re.match(line)
             if tag_match:
                  row_data["Type"] = "Tagline"

             if line == "Load more" or line.endswith(" entries"):
                  row_data["Type"] = "Meta"

             if line.startswith("Play") and "0:00" in line:
                 row_data["Type"] = "Media Reference"

             row_data["Associated_Text"] = line
             results.append(row_data)
             last_link_info = None # Reset

    else: # Simple text line
        row_data["Type"] = "Text"
        # Check for taglines
        tag_match = tagline_re.match(line)
        if tag_match:
            row_data["Type"] = "Tagline"

        if line == "Load more" or line.endswith(" entries"):
            row_data["Type"] = "Meta"

        if line.startswith("Play") and "0:00" in line:
            row_data["Type"] = "Media Reference"


        row_data["Associated_Text"] = line
        results.append(row_data)
        last_link_info = None # Reset

# --- Generate CSV Output ---
output = io.StringIO() # Write to string buffer
fieldnames = [
    "Type", "Date", "Parent_Heading", "Title/Heading", "Image_URL",
    "Image_Caption/Description", "Link_URL", "Link_Text/Context", "Associated_Text"
]
writer = csv.DictWriter(output, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)

writer.writeheader()
writer.writerows(results)

# Print the CSV output
print(output.getvalue())

# Optional: Write to a file
# with open('gentle_systems_data.csv', 'w', newline='', encoding='utf-8') as f:
#     writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
#     writer.writeheader()
#     writer.writerows(results)
# print("\nCSV data saved to gentle_systems_data.csv")