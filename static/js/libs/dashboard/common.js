
import {
    Enum
} from './utils.js';



const LINE_ID = {
    NONE: 0,
    FIRST: 1,
    DOUBLE: 2,
    THIRD: 3,
    FOUR: 4,
    FIVE: 5,
    MAX_LINES: 5
};


const JOB_DAY_TYPE = Enum({
    TYPE_DAY: 1,
    TYPE_NIGHT: 2,
    TYPE_NONE: 0});



export {
    LINE_ID,
    JOB_DAY_TYPE,

}
