// REPERTOIRE MIXITUP
$(function(){
  $('.mixitup-rep').mixItUp({
  animation: {
    effects: 'fade scale',
  },
  layout: {
    display: 'block',
  },
  selectors: {
    target: '.rep',
    filter: '.filter-rep',
  }
  });
});

// PERFORMANCES MIXITUP
$(function(){
  $('.mixitup-event').mixItUp({
  animation: {
  	effects: 'fade scale',
  },
  layout: {
  	display: 'block',
  },
  load: {
  	filter: '.recent',
  },
  selectors: {
  	target: '.performance',
  	filter: '.filter-event',
  }
  });
});
