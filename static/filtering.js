//This function runs when "submit" is clicked in the filter dropdown menu. Exercises are filtered by whichever checkboxes were checked.
function filterExercises(exercisesArray) {
    // Get all checkboxes
    var exercise_abs = document.getElementById("exercise_abs");
    var exercise_arms = document.getElementById("exercise_arms");

    var filtered_exercises = [];
    // Gather exercises from ones that are checked
    if (exercise_abs.checked == true){
        // TODO: add ab exercises to filtered_exercises array
        alert("added abs");
    }
    if (exercise_arms.checked == true){
        // TODO: add arm exercises to filtered_exercises array
        alert("added arms");
    }

    //pass filtered array back to exercises.html somehow and render html page with filtered exercises
  }

  function filterEquipment(){
      
  }

  function filterChannels(){

  }

  function sortAscending(){

  }

  function sortDescending(){
      
}