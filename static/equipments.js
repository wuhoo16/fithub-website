// Read checkbox values from local storage and store into dictionary variable. If key does not exist in storage, init an empty dictionary.
var checkboxValues = JSON.parse(
  localStorage.getItem("equipmentsCheckboxValues")
);
if (checkboxValues === null) {
  checkboxValues = {};
}

document.addEventListener("DOMContentLoaded", () => {
  // On DOM load, check the metadata with id resetLocalStorageFlag. If set to 1 then call the resetFreshState() js function
  if($('#resetLocalStorageFlag').data().flag == 1) {
    resetLocalStorage();
  }

  // on DOM load, set the sort and search bar to match localStorage state
    $("#searchBar").val(localStorage.getItem("equipmentsSearchPhrase"));
    if (localStorage.getItem("equipmentsSortPhrase") == null || localStorage.getItem("equipmentsSortPhrase") == "null") {
        $("#equipmentsSortCriteriaMenu").val("select");
    }
    else {
        $("#equipmentsSortCriteriaMenu").val(localStorage.getItem("equipmentsSortPhrase"));
    }

  // For each checkbox, persist the checkbox state based on the previous state stored in local storage
  $.each(checkboxValues, function (key, value) {
    $("#" + key).prop("checked", value);
  });
});


// Before form submission, save all checkbox's state to local storage
function saveCheckBoxStateToLocalStorage() {
  let checkboxes = $(":checkbox");
  checkboxes.each(function () {
    checkboxValues[this.id] = this.checked;
  });
  localStorage.setItem(
    "equipmentsCheckboxValues",
    JSON.stringify(checkboxValues)
  );
}

// If Reset button used for submission, reset all the checkboxes' checked attributes to false
function resetFreshState() {
  resetSearchSort();
  let checkboxes = $(":checkbox");
  checkboxes.each(function () {
    this.checked = false; // Set every checked attribute to 'false' for each checkbox element
  });
  saveCheckBoxStateToLocalStorage();
  resetArrayState();
}

function resetLocalStorage() {
  resetSearchSort();
  let checkboxes = $(":checkbox");
  checkboxes.each(function () {
    this.checked = false; // Set every checked attribute to 'false' for each checkbox element
  });
  saveCheckBoxStateToLocalStorage();
}

function resetArrayState() {
  // This will reload the model page with a fresh array
  $('#navEquipments')[0].click();
}

// If filter button used for submission, check if at least 1 checkbox is selected before submitting the form. Else, alert and do not submit
function verifyCheckBoxes(formID) {
  let isChecked = false;
  let form = document.getElementById(formID);

  for (var i = 0; i < form.elements.length; i++) {
    if (form.elements[i].type == "checkbox") {
      if (form.elements[i].checked == true) {
        isChecked = true;
        break;
      }
    }
  }

  // Do not submit form if none of the checkboxes are selected
  if (isChecked == false) {
    alert("ERROR! You must select at least one checkbox in the filter pane!");
  } else {
    // else, submit form
    saveCheckBoxStateToLocalStorage();
    form.submit();
  }
}

function resetSearchSort() {
  localStorage.setItem("equipmentsSearchPhrase", "");
  localStorage.setItem("equipmentsSortPhrase", "select");
  $("#menu").hide();
  $("#equipmentsSearchItems").val("");
  $('#searchBar').val("");
}
