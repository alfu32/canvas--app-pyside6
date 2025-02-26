from Drawable import SelectDrawable
from Tool import MultipointModifierTool, BoxDrawableTool
from Drawable import LinkDrawable
from Tool import MultipointTool

select_tool=MultipointModifierTool("Select", SelectDrawable)
drawable_box_tool=BoxDrawableTool()
link_box_tool=MultipointTool("Link", LinkDrawable)