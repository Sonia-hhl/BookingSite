document.addEventListener('DOMContentLoaded', function () {
  const reservationType = document.querySelector('#id_reservation_type');
  const roomField = document.querySelector('.form-row.field-room');
  const flightField = document.querySelector('.form-row.field-flight');
  const tourField = document.querySelector('.form-row.field-tour');
  const seatField = document.querySelector('.form-row.field-seat');

  function toggleFields() {
    const selected = reservationType.value;

    if (roomField) roomField.style.display = (selected === 'HOTEL') ? 'block' : 'none';
    if (flightField) flightField.style.display = (selected === 'FLIGHT') ? 'block' : 'none';
    if (tourField) tourField.style.display = (selected === 'TOUR') ? 'block' : 'none';
    if (seatField) seatField.style.display = (selected === 'FLIGHT') ? 'block' : 'none';  
  }

  if (reservationType) {
    toggleFields(); 
    reservationType.addEventListener('change', toggleFields);
  }
});
console.log("Reservation admin JS loaded!");


