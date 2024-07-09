# distutils: language=c++
from libc.stdint cimport uint64_t
from libcpp.vector cimport vector

cdef class HiBitset:
    cdef vector[uint64_t] layer0
    cdef vector[uint64_t] layer1
    cdef vector[uint64_t] layer2
    cdef vector[uint64_t] layer3

    def __init__(self):
        self.layer0 = vector[uint64_t]()
        self.layer1 = vector[uint64_t]()
        self.layer2 = vector[uint64_t]()
        self.layer3 = vector[uint64_t]()

    cpdef void add(self, uint64_t idx):
        # Расширить слои, если необходимо
        self.ensure_capacity(idx)
        # Установить бит в слое 0
        cdef uint64_t word_idx = idx >> 6
        cdef uint64_t bit_idx = idx & 63
        self.layer0[word_idx] |= (1 << bit_idx)
        # Обновить верхние слои
        self.update_layers(word_idx)

    cpdef void remove(self, uint64_t idx):
        self.ensure_capacity(idx)
        # Сбросить бит в слое 0
        cdef uint64_t word_idx = idx >> 6
        cdef uint64_t bit_idx = idx & 63
        self.layer0[word_idx] &= ~(1 << bit_idx)
        # Обновить верхние слои
        self.update_layers(word_idx)

    cpdef bint contains(self, uint64_t idx):
        # Проверить наличие бита
        cdef uint64_t word_idx = idx >> 6
        if word_idx >= self.layer0.size():
            return False
        cdef uint64_t bit_idx = idx & 63
        return (self.layer0[word_idx] & (1 << bit_idx)) != 0

    cdef void update_layers(self, uint64_t word_idx):
        # Обновить слои 1-3
        cdef uint64_t layer_idx
        cdef vector[uint64_t] *current_layer
        cdef vector[uint64_t] *upper_layer
        for layer_idx in range(3):
            if layer_idx == 0:
                current_layer = &self.layer0
                upper_layer = &self.layer1
            elif layer_idx == 1:
                current_layer = &self.layer1
                upper_layer = &self.layer2
            else:
                current_layer = &self.layer2
                upper_layer = &self.layer3

            if word_idx >= current_layer[0].size():
                break
            if current_layer[0][word_idx] != 0:
                upper_layer[0][word_idx >> 6] |= (1 << (word_idx & 63))
            else:
                upper_layer[0][word_idx >> 6] &= ~(1 << (word_idx & 63))
            word_idx >>= 6

    cdef void ensure_capacity(self, uint64_t idx):
        # Убедиться, что слои достаточно велики для индекса
        cdef uint64_t word_idx = idx >> 6
        while self.layer0.size() <= word_idx:
            self.layer0.push_back(0)
        word_idx >>= 6
        while self.layer1.size() <= word_idx:
            self.layer1.push_back(0)
        word_idx >>= 6
        while self.layer2.size() <= word_idx:
            self.layer2.push_back(0)
        word_idx >>= 6
        while self.layer3.size() <= word_idx:
            self.layer3.push_back(0)
