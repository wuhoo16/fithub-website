function verifyCheckBoxesAndSubmit(formID) {
    var isChecked = false;
    var form = document.getElementById(formID);

    for (var i = 0; i < form.elements.length; i++ ) {
        if (form.elements[i].type == 'checkbox') {
            if (form.elements[i].checked == true) {
                isChecked = true;
                break;
            }
        }
    }

    // Do not submit form if none of the checkboxes are selected
    if (isChecked == false) {
        alert('ERROR! You must select at least one checkbox to filter with!');
    }
    else {  // else, submit form
        form.submit();
    }
}
