// Clear filtering keys from the localStorage if the server is restarted. This ensures checkboxes are reset.
function clearLocalStorage(exerciseFilterIsActive, equipmentFilterIsActive, channelsFilterIsActive) {
    console.log('Running js clearLocalStorage() function...')
    if (!exerciseFilterIsActive) {
        localStorage.removeItem('exercisesCheckboxValues')
        console.log("Successfully cleared the key 'exercisesCheckboxValues' from browser's local storage!")
    }
    if (!equipmentFilterIsActive) {
        localStorage.removeItem('equipmentsCheckboxValues')
        console.log("Successfully cleared the key 'equipmentsCheckboxValues' from browser's local storage!")
    }
    if (!channelsFilterIsActive) {
        localStorage.removeItem('channelsCheckboxValues')
        console.log("Successfully cleared the key 'channelsCheckboxValues' from browser's local storage!")
    }
}