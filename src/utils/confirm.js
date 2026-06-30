import { ref } from 'vue';

export const confirmState = ref({
  isOpen: false,
  message: '',
  resolve: null
});

export const showConfirm = (message) => {
  return new Promise((resolve) => {
    confirmState.value = {
      isOpen: true,
      message,
      resolve
    };
  });
};

export const closeConfirm = (result) => {
  if (confirmState.value.resolve) {
    confirmState.value.resolve(result);
  }
  confirmState.value.isOpen = false;
};
