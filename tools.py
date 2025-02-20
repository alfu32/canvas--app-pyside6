from Drawable import SelectDrawable
from Tool import MultipointModifierTool
from Drawable import BoxDrawable
from Tool import MultipointTool
from Drawable import LinkDrawable
from Tool import MultipointTool

select_tool=MultipointModifierTool("Select", SelectDrawable)
drawable_box_tool=MultipointTool("Box", BoxDrawable)
link_box_tool=MultipointTool("Link", LinkDrawable)