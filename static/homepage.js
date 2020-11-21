// Clear filtering keys from the localStorage if the server is restarted. This ensures checkboxes are reset.
function clearLocalStorage(
  exerciseFilterIsActive,
  equipmentFilterIsActive,
  channelFilterIsActive,
  exerciseSearchIsActive,
  equipmentSearchIsActive,
  channelSearchIsActive,
  exerciseSortIsActive,
  equipmentSortIsActive,
  channelSortIsActive
) {
  console.log("Running js clearLocalStorage() function...");
  if (!exerciseFilterIsActive) {
    localStorage.removeItem("exercisesCheckboxValues");
    console.log(
      "Successfully cleared the key 'exercisesCheckboxValues' from browser's local storage!"
    );
  }
  if (!equipmentFilterIsActive) {
    localStorage.removeItem("equipmentsCheckboxValues");
    console.log(
      "Successfully cleared the key 'equipmentsCheckboxValues' from browser's local storage!"
    );
  }
  if (!channelFilterIsActive) {
    localStorage.removeItem("channelsCheckboxValues");
    console.log(
      "Successfully cleared the key 'channelsCheckboxValues' from browser's local storage!"
    );
  }
  if (!exerciseSearchIsActive) {
    localStorage.removeItem("exercisesSearchPhrase");
    console.log(
      "Successfully cleared the key 'exercisesSearchPhrase' from browser's local storage!"
    );
  }
  if (!equipmentSearchIsActive) {
    localStorage.removeItem("equipmentsSearchPhrase");
    console.log(
      "Successfully cleared the key 'equipmentsSearchPhrase' from browser's local storage!"
    );
  }
  if (!channelSearchIsActive) {
    localStorage.removeItem("channelsSearchPhrase");
    console.log(
      "Successfully cleared the key 'channelsSearchPhrase' from browser's local storage!"
    );
  }
  if (!exerciseSortIsActive) {
    localStorage.removeItem("exercisesSortPhrase");
    console.log(
      "Successfully cleared the key 'exercisesSortPhrase' from browser's local storage!"
    );
  }
  if (!equipmentSortIsActive) {
    localStorage.removeItem("equipmentsSortPhrase");
    console.log(
      "Successfully cleared the key 'equipmentsSortPhrase' from browser's local storage!"
    );
  }
  if (!channelSortIsActive) {
    localStorage.removeItem("channelsSortPhrase");
    console.log(
      "Successfully cleared the key 'channelsSortPhrase' from browser's local storage!"
    );
  }
}
