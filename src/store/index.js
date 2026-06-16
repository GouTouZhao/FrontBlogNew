import { ref, computed } from 'vue';
import { mockBlogData } from '../data/mock';

export const currentPartition = ref(null);
export const currentPage = ref(1);
export const itemsPerPage = 8;

export const currentList = computed(() => {
  if (!currentPartition.value) return [];
  return mockBlogData[currentPartition.value] || [];
});

export const totalPages = computed(() => {
  return Math.ceil(currentList.value.length / itemsPerPage) || 1;
});

export const paginatedList = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return currentList.value.slice(start, end);
});

export const hasPrevPage = computed(() => currentPage.value > 1);
export const hasNextPage = computed(() => currentPage.value < totalPages.value);
export const isEmpty = computed(() => currentList.value.length === 0);

export const prevPage = () => {
  if (hasPrevPage.value) {
    currentPage.value--;
  }
};

export const nextPage = () => {
  if (hasNextPage.value) {
    currentPage.value++;
  }
};
