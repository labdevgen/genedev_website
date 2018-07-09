var maxPlasmidId = 1 
var maxWellId = 1 

var DNA_PRO_1CM2=undefined
var OPTIMEM_DILUTION_VOLUM_PRO_CM2=undefined
var P3000_pro_1000ng_DNA=2
var Lipofectamin_pro_cm2=undefined

var del_pl_click_function=function(event){
	$(this).parents(".cPlasmidTR").remove()
	if ($(".cPlasmidTR").length <= 1){
		$(".cPlasmidDel").prop('disabled',true);
	}
}

function get_object_keys(obj){ //return all keys of obj as an array
	r=[]
	for (k in obj)	 {r.push(k)}
	return r
}

function split_id_txt_and_number(id){
	var i = id.length
	do
	{
		i -= 1
	}
	while ((i>0) && (!isNaN(id[i])))
	
	if (i==(id.length-1))
	{
		return [id,undefined]
	}
	else if (i<0)
	{
		return [undefined,id]
	}
	else
		return [id.slice(0,i),id.slice(i+1,id.length)]
}

function set_all_elements_ids(element, id_number) {
	$(element).find("*").each(function(){
			var id_old=$(this).attr("id")
			if (typeof(id_old) != 'undefined')
			{
				var id_old_splited = split_id_txt_and_number(id_old)
				if (typeof(id_old_splited[0]) != 'undefined' && typeof(id_old_splited[1]) != 'undefined')
				{
					$(this).attr("id",id_old_splited[0]+id_number)
				}
			}
	})
	return 0
}

var add_pl_click_function=function(event){
		maxPlasmidId += 1
		var last_ind = maxPlasmidId
	
		var newtr=$("#tablePlasmids tr:last").clone(withDataAndEvents=true)
		set_all_elements_ids(newtr,last_ind)
		$("#tablePlasmids").append(newtr)
	
		$(".cPlasmidDel").prop('disabled', false);
	}

var del_well_click_function=function(event){
	$(this).parents(".cPlateTR").remove()
	if ($(".cPlateTR").length <= 1){
		$(".cWellDel").prop('disabled',true);
	}
}

var add_well_click_function=function(event){
		/*find the last id index*/
		maxWellId += 1
		var last_ind = maxWellId
		
		/*add one more row to wells table*/
		var newtr=$("#tablePlates tr:last").clone(withDataAndEvents=true)
		set_all_elements_ids(newtr,last_ind)
		$(newtr).find(".cWellId").empty().append(last_ind)
		$("#tablePlates").append(newtr)
		$(".cWellDel").prop('disabled', false);
	}

var plasmids = new Object //stores info about plasmids. Updates by validate_plasmids() func
//type structure plasmids={id:{name:name,pl_conc:concentration}}

function validate_plasmids(){
	plasmids=new Object
	$("#tablePlasmids").find(".cPlasmidTR").each(function(){
		var pl_index=$(this).find(".cPlasmidName").attr("id")
		pl_index=split_id_txt_and_number(pl_index)[1]
		pl_name=$(this).find(".cPlasmidName").val()
		pl_conc=$(this).find(".cPlasmidConc").val()

		if (isNaN(pl_conc) || (pl_conc==""))
			$(this).find(".cPlasmidConc").addClass("unvalid_plasmid")
		else if (pl_name=="")
			$(this).find(".cPlasmidName").addClass("unvalid_plasmid")
		else
			plasmids[pl_index]={name:pl_name,pl_conc:parseFloat(pl_conc)}
	})
	return plasmids
}

var main_calculator=function(wells,current_volume,liquid_name,do_aliqout,must_open_tr){
	//wells contian all info about wells we are going to transfect
	//wells structure:
	//wells={id:{well_removed_plasmids:array_of_indexes_of_plasmids that were analyzed on prev step
	//			well_plasmids:array_of_indexes_of_plasmid_obj,
	//			 well_plasmid_ratios:array_of_floats,
	//			 well_scaling_factor:float}}
	//current_volume - (int of float) volume of liquid (Opti-MEM or mixture Opti-MEM+plasmids) we have at current step
	//if current_volume==-1 it means we are at the first enterance and we need to calculate total amount of Opti-MEM needed for transfection
	//liquid_name - str, it will be reported in a sentences like dilute xxx uL of plasmids in yyy uL of liquid_name. Supposed to be Opti-MEM or "mixture" (means Opti-MEM+some plasmids diluted there before)
	//do_aliqout - whether in new tubes shoud be aliqoted (true) or left in current tube
	//must_open_tr - bool, whether this function shell open <tr> in the begining and close </tr> in the end of function
	
	function characterize_theMost_ubiquitus_plasmid(wells){ // returns the obj characterizin most ubiq plsmid
		var indexes=new Object
		var indmax=new Object
		indmax.index=-1 // index of plasmid
		indmax.occurance=[] // array contain indexes of wells where plasmid needed
		indmax.ug=-1 // amount of cm2 to transfect with this plasmid (accountig for ratio of different plasmids in wells), used to calculate amount of DNA
		indmax.cm2_not_counting_plasmids_ratio = -1 // total amount of cm2 to transfect with this plasmid, used to calculate volume of diluant for all wells
		indmax.minug=0 // this amount of plasmid that we need to add into those well, where minimum amount of this plasmid needed
		var total_cm2=0
		for (i in wells){
			var total_plasmids_ratio_in_well=0
			total_cm2+=wells[i].scaling_factor
//			for (j=0;j<wells[i].well_plasmids.length;j++){
//				total_plasmids_ratio_in_well += wells[i].well_plasmids_ratios[j]
//			}
			for (j=0;j<wells[i].well_plasmids.length;j++){
				ind=wells[i].well_plasmids[j]
//				if ($.inArray(ind,wells[i].well_removed_plasmids) == -1){
				if (wells[i].well_plasmids_ug[j] > 0){	
					if (typeof(indexes[ind])=='undefined') {
						indexes[ind] = {occurance:[i],
//										cm2:(wells[i].scaling_factor*(wells[i].well_plasmids_ratios[j]/total_plasmids_ratio_in_well)),
										ug:wells[i].well_plasmids_ug[j],
										minug:wells[i].well_plasmids_ug[j],
										cm2_not_counting_plasmids_ratio:(wells[i].scaling_factor)}
					}
					else {
						indexes[ind].occurance.push(i)
//						indexes[ind].cm2 += wells[i].scaling_factor*(wells[i].well_plasmids_ratios[j]/total_plasmids_ratio_in_well)
						indexes[ind].ug += wells[i].well_plasmids_ug[j]
						indexes[ind].minug = Math.min(wells[i].well_plasmids_ug[j],indexes[ind].minug)
						indexes[ind].cm2_not_counting_plasmids_ratio += wells[i].scaling_factor
					}
					if (indmax.occurance.length < indexes[ind].occurance.length) {
						indmax.index=ind
						indmax.occurance=indexes[ind].occurance.slice()
//						indmax.cm2=indexes[ind].cm2
						indmax.ug=indexes[ind].ug
						indmax.minug=indexes[ind].minug
						indmax.cm2_not_counting_plasmids_ratio=indexes[ind].cm2_not_counting_plasmids_ratio
					}
				}
			}
		}
		indmax.total_cm2=total_cm2
		return indmax
	}
	
	function remove_wells(current_wells,toremove_wells_indexes_array){ // returns new wells obj without deleted items
		var r=new Object
		for (i in current_wells){
			if ($.inArray(i,toremove_wells_indexes_array) == -1){
				r[i]=current_wells[i]}
		}
		return r
	}

	function filter_wells(current_wells,ubi_plasmid){ //leaves only wells with selected in array indexes
		var r=new Object
		var toleave_wells_indexes_array = ubi_plasmid.occurance
		for (i in current_wells){
			if ($.inArray(i.toString(),toleave_wells_indexes_array) != -1){
				r[i]=current_wells[i]
				r[i].well_plasmids_ug[$.inArray(ubi_plasmid.index,r[i].well_plasmids)] -= ubi_plasmid.minug
			}
		}
		return r
	}
	
//	function remove_plasmid(wells,pl_id){
//		for (i in wells)
//			wells[i].well_removed_plasmids.push(pl_id)
//	}
	console.info("===========in main calculator=======")
	var ubi_plasmid=characterize_theMost_ubiquitus_plasmid(wells)
	console.info("wells")
	console.info(wells)
	console.info("ubi_plasmid")
	console.info(ubi_plasmid)
	console.info("current_volume")
	console.info(current_volume)	
	
	if (current_volume==-1) {current_volume=OPTIMEM_DILUTION_VOLUM_PRO_CM2*ubi_plasmid.total_cm2}
	console.info("current_volume")
	console.info(current_volume)	
	
	if (ubi_plasmid.index == -1){
		// there are no more plasmids to analyze.
		var k=get_object_keys(wells)
		if (k.length==0)
			{return ""} // RECURSION EXIT
		else if (k.length==1){ // we have only one well
				var r=""
				current_volume=Math.round(current_volume*100)/100
				console.info(wells)
				if (must_open_tr) {r+="<table class='plasmid_dilution_table'><tr>"}
				if (do_aliqout){
					r+="<td>Aliqout "+
					Math.round(current_volume*100)/100+
					"uL of "+liquid_name+
					"<br>Add "+Math.round(wells[k[0]].scaling_factor*(DNA_PRO_1CM2/1000)*P3000_pro_1000ng_DNA*100)/100+
					"uL of P3000 reagent<br>"+
					"<span class='ready_tube_name'>Tube "+
					k[0]+"</span> ("+current_volume+"uL) ready. Vortex.</td>"
				}
				else{
					r+="<td><br>"+
					"Add "+Math.round(wells[k[0]].scaling_factor*(DNA_PRO_1CM2/1000)*P3000_pro_1000ng_DNA*100)/100+
					"uL of P3000 reagent<br>"+
					"<span class='ready_tube_name'>Tube "+
					k[0]+"</span> ("+current_volume+"uL) ready. Vortex</td>"
				}
				if (must_open_tr) {r+="</tr></table>"}
				return r // RECURSION EXIT
			}
		else
		{
			var total_cm2=0
			for (i in wells){total_cm2 +=wells[i].scaling_factor}
			var r=""
			if (must_open_tr) {r+="<table class='plasmid_dilution_table'><tr>"}
			for (i in wells){
				var v=Math.round(current_volume*wells[i].scaling_factor*100/total_cm2)/100
				r+= "<td>Aliqout "+v+"uL of "+liquid_name+"<br>"+
				"Add "+Math.round(wells[i].scaling_factor*(DNA_PRO_1CM2/1000)*P3000_pro_1000ng_DNA*100)/100+
				"uL of P3000 reagent. Vortex<br>"+
				"<span class='ready_tube_name'>Tube "+i+"</span> ready</td>"
			}
			if (must_open_tr) {r+="</tr></table>"}
			return r // RECURSION EXIT
		}
	} 
	
	var r=""
	if (must_open_tr) {r+="<table class='plasmid_dilution_table'><tr>"}
	
	var dna_amount_uL = Math.round(100*(ubi_plasmid.minug*ubi_plasmid.occurance.length)/plasmids[ubi_plasmid.index].pl_conc)/100
//	var dna_amount_uL=Math.round(100*(DNA_PRO_1CM2*ubi_plasmid.cm2)/plasmids[ubi_plasmid.index].pl_conc)/100	
	var volume_for_ubi_DNA=Math.round(current_volume*(ubi_plasmid.cm2_not_counting_plasmids_ratio/ubi_plasmid.total_cm2)*100)/100

	console.info("current_volume")
	console.info(current_volume)
	

	console.info("ubi_plasmid")
	console.info(ubi_plasmid)
	
	console.info("volume_for_ubi_DNA")
	console.info(volume_for_ubi_DNA)
	
	r+="<td>Dilute <span class='dna_amount_uL'>"+dna_amount_uL+"uL</span> of plasmid <span class='plasmid_name'>"+plasmids[ubi_plasmid.index].name+"</span> in "+volume_for_ubi_DNA+"uL of "+liquid_name+". Vortex.<br>"

	var new_wells=filter_wells(wells,ubi_plasmid)
	var do_aliqout_at_next_step=!(get_object_keys(new_wells).length==get_object_keys(wells))
//	remove_plasmid(new_wells,ubi_plasmid.index)
	console.info(new_wells)
	r+=main_calculator(new_wells,volume_for_ubi_DNA+dna_amount_uL,"mixture",false,true) //FIRST RECURSION IN
	r+="</td>"

	new_wells2=remove_wells(wells,ubi_plasmid.occurance)
	do_aliqout_at_next_step=!(get_object_keys(new_wells2).length==get_object_keys(wells))

	r+=main_calculator(new_wells2,current_volume-volume_for_ubi_DNA,liquid_name,do_aliqout_at_next_step,false) //FIRST RECURSION IN	
	
	if (must_open_tr) {r+="</tr></table>"}
	return r;
}
	

function generate_wells_object(){
	var wells=new Object
	$("#tablePlates").find(".cPlateTR").each(function(){
		index=split_id_txt_and_number($(this).find("select").attr("id"))[1]
		scaling_factor=parseFloat($(this).find("select").val())
//		well_removed_plasmids=[]
		well_plasmids_ratios=[]
		well_plasmids_ug=[]
		well_plasmids=[]
		total_well_ratio = 0
		$(this).find(".cPlasmidCheckbox").each(function(){
			if ($(this).prop("checked"))
			{
				well_plasmids.push($(this).val())
				plasmid_ratio = parseFloat($(this).next("span").find("input").val())
				well_plasmids_ratios.push(plasmid_ratio)
				total_well_ratio += plasmid_ratio
			}
		})
		for (var i=0; i<well_plasmids_ratios.length;i++){
			well_plasmids_ug.push(scaling_factor*DNA_PRO_1CM2*well_plasmids_ratios[i]/total_well_ratio)
		}
		wells[index]={"scaling_factor":scaling_factor,
						"well_plasmids_ug":well_plasmids_ug,
						"well_plasmids":well_plasmids}
//						"well_removed_plasmids":well_removed_plasmids}
	})
	console.info("Wells generated:")
	console.info(wells)
	return wells
}

function read_transfectant_parameters(){
	var transfectant=$("#Transfectant").val()
	if (transfectant != "Lip3000")
		return -1
	DNA_PRO_1CM2=parseFloat($("#DNA_pro_1cm2").val())
	OPTIMEM_DILUTION_VOLUM_PRO_CM2=parseFloat($("#OptiMem_pro_cm2").val())
	Lipofectamin_pro_cm2=parseFloat($("#Lipofectamin_pro_cm2").val())
	return 0
}

function lipofectamin_dilution_calculator(wells){
	var total_cm2 = 0
	for (i in wells)
		total_cm2 += wells[i].scaling_factor
	var r="Dilute "+total_cm2*Lipofectamin_pro_cm2+"uL of lipofectamin in "+
			total_cm2*OPTIMEM_DILUTION_VOLUM_PRO_CM2+"uL of Opti-MEM.<br>Vortex briefly or mix by pipeting.<br>"
	
	r += "Combine Lipofectamin and plasmids: <br><table id='tableLipofectaminAndPlasmids' class='plasmid_dilution_table'>"
	for (i in wells){
		r += "<tr><td>Tube "+i+"</td><td>Add "+
			wells[i].scaling_factor*OPTIMEM_DILUTION_VOLUM_PRO_CM2+
			"uL of diluted lipofectamin</td><td>Mix by pipeting</td></tr>"
	}
	r += "</table>"
	r += "Incubate DNA/Lipofectamin complex for 5 min at RT.<br>Applay to cells"
	return r
}
$(function(){
	$(".cPlasmidAdd").click(add_pl_click_function)
	$(".cPlasmidDel").click(del_pl_click_function)
	$(".cWellAdd").click(add_well_click_function)
	$(".cWellDel").click(del_well_click_function)	
	
	$(".cPlasmidConc").change(function(event){
		$(this).removeClass("unvalid_plasmid")
	})
	
	$(".cPlasmidName").change(function(event){
		$(this).removeClass("unvalid_plasmid")
	})
	
	$("#update_plasmids").click(function (event){
		 var plasmids=validate_plasmids() // get all valid plasmid. Structure of array described before
		 var new_plasmid_idxs=get_object_keys(plasmids) // idxs of all avaliable plasmids
		 var table_elements=$("#tablePlates").find(".cPlasmids_in_well") // all elements of wells table with checkboxes corresponding to plasmids
		 var current_plasmid_idxs=[] // all plasmids that are currently displayed as checkboxes will be in this array

		 table_elements.first().find(".cPlasmidCheckbox").each(function(){ //filling array using first row in wells table 
			 	current_plasmid_idxs.push($(this).val())		 
			})
		 
		 var idxs_to_del = $.except(current_plasmid_idxs,new_plasmid_idxs)
		 var idxs_to_add = $.except(new_plasmid_idxs,current_plasmid_idxs)
		 var idxs_to_leave=$.intersect(current_plasmid_idxs,new_plasmid_idxs)
		 
		 //removeing elements
		 for (i=0;i<idxs_to_del.length;i++){
			 var temp=table_elements.find(".cPlasmidCheckbox[value="+idxs_to_del[i]+"]")
			 temp.next("span").remove()
			 temp.remove()
		}

		//changing plasmid names if needed
		for (i=0;i<idxs_to_leave.length;i++){ 
			var temp=table_elements.find(".cPlasmidCheckbox[value='"+idxs_to_leave[i]+"']")
			temp.next("span").remove()
			temp.after('<span>'+plasmids[idxs_to_leave[i]].name+' ratio: <input type="text" value="1" size=2/><br></span>')
		}
		
		 //adding new elements
		 for (i=0;i<idxs_to_add.length;i++){ 
			 var idx=idxs_to_add[i]
			 table_elements.each(function(){
					s='<div><input type="checkbox" value="'+idx+'" class="cPlasmidCheckbox" checked/><span>'+plasmids[idx].name+' ratio: <input type="text" value="1" size=3/><br></span>'
					$(this).append(s)
				})
		}
		 
	})
	
	$("#calculate").click(function(element){
		if (read_transfectant_parameters() == -1){
			alert("Unknown transfectant");
			return -1
		}
		wells=generate_wells_object()
		res=main_calculator(wells,-1,"Opti-MEM",false,true)
		$("div#Plasmid_dilutioin_map").empty().append("<h1>Step1. Prepare plasmids mix</h1><br>"+res)
		res=lipofectamin_dilution_calculator(wells)
		res = "<h1>Step2. Dilute lipofectamin and mix with plasmids</h1><br>"+res
		$("div#Plasmid_dilutioin_map").append(res)
	})

	$("#show_additional_params").click(function(element){
		var transfectant=$("#Transfectant").val()
		var d=$("div[data-transfectant="+transfectant+"]")
		$(d).toggle()
		if ($(d).is(':hidden'))
		{
			$("#show_additional_params_img").attr("src","img/hidden.jpg")
		}
		else
		{
			$("#show_additional_params_img").attr("src","img/shown.jpg")
		}
		return false
	})
	
	$("#addNewPlate").click(function(element){
		var n=$("#newPlateTypeName").val()
		var sf=parseFloat($("#newPlateScalingFactor").val())
		$("select.SelectWell").each(function(){
			$(this).append("<option value='"+sf+"'>"+n+"("+sf+"cm2)"+"</option>")
		})
		alert("done!")
		$("#newPlateTypeName").val("")
		$("#newPlateScalingFactor").val("")
	})	
});