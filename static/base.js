// Submit the sort form given the formID, hiddenFieldID, and 'ascending'/'descending' value
function submitSortForm(sortFormID, hiddenFieldID, value) {
  let form = document.getElementById(sortFormID);
  let selectMenu = form.getElementsByTagName('SELECT')[0]
  let selectedSortingAttribute = selectMenu.options[selectMenu.options.selectedIndex];
  if (selectedSortingAttribute.value == 'select') {
      alert('ERROR! Please select a sorting criteria from the "Sort By" drop-down menu before sorting!')
  }
  else { // Only submit the sort form if the active selected option is not the default 'Sort By'
      let hiddenField = document.getElementById(hiddenFieldID);
      hiddenField.value = value;
      form.submit();
  }
}

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