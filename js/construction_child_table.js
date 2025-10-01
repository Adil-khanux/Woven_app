frappe.ui.form.on("Item",{
    // By default Special Construction Child Table is Hide
    onload (frm){    
        frm.toggle_display('custom_strip_color',false);
    }
});

// give Child Table Label name
frappe.ui.form.on("Special Construction" ,{
//  field name when its function will  call
    types (frm,ctd,cdn){

        toggle_strip_color(frm);
   
    }

}) ;

    function toggle_strip_color(frm) {
        let strip = false 

        for(let i=0; i < frm.doc.custom_special_construction.length; i++){
            let row = frm.doc.custom_special_construction[i];
            //  check row ki field types m value h equal y nhi and we use instead of this ==  we use === bcz its value and ddata type both check
            if ( row.types === "Side Color Stripes") {
                strip = true
                break;
            }

        }
        //  Show table 
        frm.toggle_display('custom_strip_color',strip)

    }

//  using for each loop 

// 2. (frm.doc.custom_special_construction || []).forEach(function(row) {
//     if (row.types === "Side Color Stripes") {
//         showStrip = true;
//     }
// });



//  using some which is shorthand of forEach loop
// 3. function toggle_strip_color(frm) {
//     // Check if any row has types === "Side Color Stripes"
//     let showStrip = (frm.doc.custom_special_construction || []).some( => here we use some instead of forEach(function (row){})<=
//         row => row.types === "Side Color Stripes"
//     );

//     // Show/hide the field based on condition
//     frm.toggle_display("custom_strip_color", showStrip);
// }