// Read checkbox values from local storage and store into dictionary variable. If key does not exist in storage, init an empty dictionary.
var checkboxValues = JSON.parse(localStorage.getItem('exercisesCheckboxValues'));
if (checkboxValues === null){
  checkboxValues = {};
}

document.addEventListener('DOMContentLoaded', () => {
    // For each checkbox, persist the checkbox state based on the previous state stored in local storage
    $.each(checkboxValues, function(key, value) {
      $("#" + key).prop('checked', value);
    });
});

// Before form submission, save all checkbox's state to local storage
function saveCheckBoxStateToLocalStorage() {
    let checkboxes = $(':checkbox');
    checkboxes.each(function() {
        checkboxValues[this.id] = this.checked;
    });
    localStorage.setItem("exercisesCheckboxValues", JSON.stringify(checkboxValues));
}

// If Reset button used for submission, reset all the checkboxes' checked attributes to false
function resetCheckboxState(formID, resetHiddenFieldID) {
    let checkboxes = $(':checkbox');
    let form = document.getElementById(formID);

    checkboxes.each(function() {
        this.checked = false;  // Set every checked attribute to 'false' for each checkbox element
    });
    saveCheckBoxStateToLocalStorage();
    document.getElementById(resetHiddenFieldID).value = 'resetClicked'
    form.submit();
}

// If filter button used for submission, check if at least 1 checkbox is selected before submitting the form. Else, alert and do not submit
function verifyCheckBoxes(formID) {
    let isChecked = false;
    let form = document.getElementById(formID);

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
        alert('ERROR! You must select at least one checkbox in the filter pane!');
    }
    else {  // else, submit form
        saveCheckBoxStateToLocalStorage();
        form.submit();
    }
}
