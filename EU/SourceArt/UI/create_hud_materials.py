"""Create Task 6 Canvas mask and vignette materials in the editor."""
import unreal,json
from pathlib import Path
at=unreal.AssetToolsHelpers.get_asset_tools();ml=unreal.MaterialEditingLibrary
folder='/Game/EscapeUnseen/UI/Materials'
unreal.EditorAssetLibrary.make_directory(folder)
def material(name):
 m=unreal.load_asset(folder+'/'+name)
 if not m:m=at.create_asset(name,folder,unreal.Material,unreal.MaterialFactoryNew())
 ml.delete_all_material_expressions(m)
 m.set_editor_property('material_domain',unreal.MaterialDomain.MD_UI)
 m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT)
 return m
def node(m,cls,x,y,**props):
 n=ml.create_material_expression(m,cls,x,y)
 for k,v in props.items():n.set_editor_property(k,v)
 return n
def link(a,out,b,pin):
 if not ml.connect_material_expressions(a,out,b,pin):raise RuntimeError('Material connection failed: '+b.get_name()+'.'+pin)
m=material('M_UIStamp')
white=unreal.load_asset('/Engine/EngineResources/WhiteSquareTexture.WhiteSquareTexture')
tex=node(m,unreal.MaterialExpressionTextureSampleParameter2D,-400,0,parameter_name='StampMask',texture=white)
tint=node(m,unreal.MaterialExpressionVectorParameter,-400,-200,parameter_name='Tint',default_value=unreal.LinearColor(1,1,1,1))
ml.connect_material_property(tex,'R',unreal.MaterialProperty.MP_OPACITY)
ml.connect_material_property(tint,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
ml.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m,False)
v=material('M_UIVignette')
uv=node(v,unreal.MaterialExpressionTextureCoordinate,-900,0)
center=node(v,unreal.MaterialExpressionConstant2Vector,-900,150,r=.5,g=.5)
dist=node(v,unreal.MaterialExpressionDistance,-700,0);link(uv,'',dist,'A');link(center,'',dist,'B')
sub=node(v,unreal.MaterialExpressionSubtract,-520,0,const_b=.225);link(dist,'',sub,'A')
div=node(v,unreal.MaterialExpressionDivide,-350,0,const_b=.275);link(sub,'',div,'A')
sat=node(v,unreal.MaterialExpressionSaturate,-180,0);link(div,'',sat,'')
alpha=node(v,unreal.MaterialExpressionMultiply,0,0,const_b=.25);link(sat,'',alpha,'A')
black=node(v,unreal.MaterialExpressionConstant,0,-150,r=0)
ml.connect_material_property(alpha,'',unreal.MaterialProperty.MP_OPACITY)
ml.connect_material_property(black,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
ml.recompile_material(v);unreal.EditorAssetLibrary.save_loaded_asset(v,False)
Path('F:/Escape Unseen/EU/Saved/codex_task6/material_report.json').write_text(json.dumps({'saved':[m.get_path_name(),v.get_path_name()]}),encoding='utf-8')
