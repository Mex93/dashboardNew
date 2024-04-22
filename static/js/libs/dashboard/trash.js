

// function getNullArrIndexesInResult5Mins(
//     arr = [],
//     start_index = 0,
//     delay_count = 0,
//     number_null = 0,
//     max_size = arr.length)
// {
//     // найдёт пустые элементы массива координат и вернёт массивов с индексами нулей
//     let currentDelayCount= 0;
//     let arr_DeletedPoints = []
//     let newArrSize = 0;
//     if((max_size > 0) && (start_index < max_size))
//     {
//         for(let i = start_index; i<max_size; i++)
//         {
//             if(number_null === arr[i])
//             {
//                 if(currentDelayCount < delay_count)
//                 {
//                     currentDelayCount++;
//                     continue;
//                 }
//                 arr_DeletedPoints[newArrSize] = i;
//                 newArrSize++;
//             }
//         }
//         if(arr_DeletedPoints.length > 0)
//         {
//             return arr_DeletedPoints;
//         }
//     }
//     return false;
// }



// export {
//    getNullArrIndexesInResult5Mins
// }

