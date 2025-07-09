__author__ = "receyuki"
__filename__ = "textbox.py"
__copyright__ = "Copyright 2023"
__email__ = "receyuki@gmail.com"

from typing import Union, Tuple, Optional
import re

from customtkinter import CTkTextbox, CTkFont

from .constants import EDITABLE, ACCESSIBLE_GRAY, LORA_TAG_HIGHLIGHT, LORA_NAME_HIGHLIGHT, LORA_WEIGHT_HIGHLIGHT


class STkTextbox(CTkTextbox):
    def __init__(
        self,
        master: any,
        width: int = 200,
        height: int = 200,
        corner_radius: Optional[int] = None,
        border_width: Optional[int] = None,
        border_spacing: int = 3,
        bg_color: Union[str, Tuple[str, str]] = "transparent",
        fg_color: Optional[Union[str, Tuple[str, str]]] = None,
        border_color: Optional[Union[str, Tuple[str, str]]] = None,
        text_color: Optional[Union[str, str]] = None,
        scrollbar_button_color: Optional[Union[str, Tuple[str, str]]] = None,
        scrollbar_button_hover_color: Optional[Union[str, Tuple[str, str]]] = None,
        font: Optional[Union[tuple, CTkFont]] = None,
        activate_scrollbars: bool = True,
        text: str = "",
        **kwargs
    ):
        # Regex pattern for lora tags
        self.lora_pattern = r'<lora:([^:]+):([^>]+)>'
        self._text = text
        self.current_text = text

        super().__init__(
            master=master,
            width=width,
            height=height,
            corner_radius=corner_radius,
            border_width=border_width,
            border_spacing=border_spacing,
            bg_color=bg_color,
            fg_color=fg_color,
            border_color=border_color,
            text_color=text_color,
            scrollbar_button_color=scrollbar_button_color,
            scrollbar_button_hover_color=scrollbar_button_hover_color,
            font=font,
            activate_scrollbars=activate_scrollbars,
            **kwargs
        )

        if text:
            self.insert("end", text)
            self.configure(state="disabled")

    @property
    def ctext(self):
        return self.get("1.0", "end")

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text: str = ""):
        self._text = text
        self.current_text = text
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.insert("end", self._text)

        # Apply lora highlighting
        self._apply_lora_highlighting(self._text)

        self.configure(state="disabled")

    def view_vertical(self):
        text = ",\n".join(
            list(
                filter(
                    None,
                    list(
                        map(
                            lambda x: x.lstrip(" "),
                            self._text.replace("\n", "").split(","),
                        )
                    ),
                )
            )
        )
        self.current_text = text
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.insert("end", text)

        # Apply lora highlighting
        self._apply_lora_highlighting(text)

        self.configure(state="disabled")

    def view_normal(self):
        self.current_text = self._text
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.insert("end", self._text)

        # Apply lora highlighting
        self._apply_lora_highlighting(self._text)

        self.configure(state="disabled")

    def sort_asc(self):
        text = "\n".join(list(filter(None, sorted(self.current_text.split("\n")))))
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.insert("end", text)

        # Apply lora highlighting
        self._apply_lora_highlighting(text)

        self.configure(state="disabled")

    def sort_des(self):
        text = "\n".join(
            list(filter(None, sorted(self.current_text.split("\n"), reverse=True)))
        )
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.insert("end", text)

        # Apply lora highlighting
        self._apply_lora_highlighting(text)

        self.configure(state="disabled")

    def sort_off(self):
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.insert("end", self.current_text)

        # Apply lora highlighting
        self._apply_lora_highlighting(self.current_text)

        self.configure(state="disabled")

    def edit_on(self):
        self.configure(state="normal")
        self.configure(text_color=EDITABLE)

    def edit_off(self):
        self.configure(state="disabled")
        self.configure(text_color=ACCESSIBLE_GRAY)

    def _apply_lora_highlighting(self, text):
        """Apply highlighting to lora tags in the text"""
        # Configure tags for different parts of lora highlighting
        self._textbox.tag_configure("lora_tag_highlight", foreground=self._apply_appearance_mode(LORA_TAG_HIGHLIGHT))
        self._textbox.tag_configure("lora_name_highlight", foreground=self._apply_appearance_mode(LORA_NAME_HIGHLIGHT))
        self._textbox.tag_configure("lora_weight_highlight", foreground=self._apply_appearance_mode(LORA_WEIGHT_HIGHLIGHT))

        # Find and highlight lora patterns: <lora:lora_name:weight>
        for match in re.finditer(self.lora_pattern, text):
            full_match = match.group(0)
            lora_name = match.group(1)
            weight = match.group(2)

            # Calculate indices for each part
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"

            # Calculate indices for lora_name
            name_start_offset = full_match.find(lora_name)
            name_start_idx = f"1.0+{match.start() + name_start_offset}c"
            name_end_idx = f"1.0+{match.start() + name_start_offset + len(lora_name)}c"

            # Calculate indices for weight
            weight_start_offset = full_match.find(weight)
            weight_start_idx = f"1.0+{match.start() + weight_start_offset}c"
            weight_end_idx = f"1.0+{match.start() + weight_start_offset + len(weight)}c"

            # Highlight the tag brackets and colons with tag color
            self._textbox.tag_add("lora_tag_highlight", start_idx, name_start_idx)  # <lora:
            self._textbox.tag_add("lora_tag_highlight", name_end_idx, weight_start_idx)  # : between name and weight
            self._textbox.tag_add("lora_tag_highlight", weight_end_idx, end_idx)  # > at the end

            # Highlight the lora_name with name color
            self._textbox.tag_add("lora_name_highlight", name_start_idx, name_end_idx)

            # Highlight the weight with weight color
            self._textbox.tag_add("lora_weight_highlight", weight_start_idx, weight_end_idx)
