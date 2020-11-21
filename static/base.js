// Submit the sort form given the formID, hiddenFieldID, and 'ascending'/'descending' value
function submitSortForm(sortFormID, hiddenFieldID, value) {
  let form = document.getElementById(sortFormID);
  let hiddenField = document.getElementById(hiddenFieldID);

  hiddenField.value = value;
  //    localStorage.setItem(sortFormID, value);
  form.submit();
}

// Ensure looping works for the homepage hype video for browsers that don't support the loop attribute
document.addEventListener("DOMContentLoaded", ensureVideoLoop);

/* Set the width of the side navigation to 250px and the left margin of the page content to 250px */
function openNav() {
  document.getElementById("mySidenav").style.width = "250px";
  document.getElementById("main").style.marginLeft = "250px";
}

/* Set the width of the side navigation to 0 and the left margin of the page content to 0 */
function closeNav() {
  document.getElementById("mySidenav").style.width = "0";
  document.getElementById("main").style.marginLeft = "0";
}

function sortAscending() {}

function sortDescending() {}
